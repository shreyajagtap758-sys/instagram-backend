from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from server.src.error_handling.exceptions.authExceptions import InvalidToken, InvalidCredentials
from server.src.repository.redis import add_to_blacklist_token
from server.src.repository.token import revoke_all_session_of_refresh_token
from server.src.repository.user import (
    get_user_by_email,
    user_creation,
    username_exists,
    RESTORE_WINDOW_DAYS,
    get_user_for_deletion_update,
    mark_user_pending_deletion,
    restore_pending_deletion_user,
    create_user_deletion_audit_event,
    get_user_for_update, update_user_account
)
from server.src.core.AuthSecurity.auth import verify_password, hash_password
from server.src import models
from server.src.models.users import USER_STATUS_ACTIVE, USER_STATUS_PURGING, USER_STATUS_PENDING_DELETION
from server.src.services.tokens import generate_tokens
from server.src.error_handling.exceptions.userExceptions import EmailAlreadyExists, UsernameNotValid, UserNotFound, UserPurgeInProgress,InvalidAccountRestoreState
from server.src.error_handling.exceptions.securityExceptions import TooManyAttempts
from server.src.utils.validations import normalize_email, validate_password, validate_username


MAX_FAILED_ATTEMPTS = 5
LOCK_UNTIL_MINUTES = 15


async def create_user(user_data, session):
    email = normalize_email(user_data.email)

    existing = await get_user_by_email(email, session)
    if existing:
        raise EmailAlreadyExists()

    username = validate_username(user_data.username)
    password = validate_password(user_data.password)

    result = await username_exists(username, session)
    if result:
        raise UsernameNotValid()

    user = models.User(email = email,username= username,hashed_password = hash_password(password))

    return await user_creation(user, session)

async def update_account(user_id, payload, session):
    user = await get_user_for_update(
        user_id=user_id,
        session=session
    )

    if not user:
        raise UserNotFound()

    if user.status not in USER_STATUS_ACTIVE:
        raise UserNotFound()

    update_data = {}

    if payload.username is not None:
        username = payload.username.strip().lower()
        validate_username(username)

        if username != user.username:
            exists = await username_exists(
                username=username,
                session=session
            )
            if exists:
                raise UsernameNotValid()

            update_data["username"] = username

    if (payload.is_private is not None
            and payload.is_private != user.is_private
    ):
        update_data["is_private"] = payload.is_private

    # idempotent request
    if not update_data:
        return {
            "id": str(user.id),
            "username": user.username,
            "is_private": user.is_private
        }

    try:
        updated_user = await update_user_account(
            user_id=user.id,
            values=update_data,
            session=session
        )

    except IntegrityError:
        raise UsernameNotValid()

    return {
        "id": str(updated_user.id),
        "username": updated_user.username,
        "is_private": updated_user.is_private
    }

async def login_user(user_data, session):
    email = normalize_email(user_data.email)

    user = await get_user_by_email(email, session)

    if not user:
        raise InvalidCredentials()

    now = datetime.now(timezone.utc)

    if user.is_locked:
        if user.lock_until > now:
            raise TooManyAttempts()
        else:
            user.is_locked = False
            user.lock_until = None
            user.failed_login_attempts = 0
            await session.commit()

    if not verify_password(user_data.password, user.hashed_password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.is_locked = True
            user.lock_until = now + timedelta(minutes=LOCK_UNTIL_MINUTES)

        await session.commit()

        raise InvalidCredentials()

    user.failed_login_attempts = 0
    user.last_login = now
    await session.commit()

    return await generate_tokens(user, session)


async def logout_user(payload: dict, session):
    jti = payload.get("jti")
    exp = payload.get("exp")
    user_id = payload.get("sub")

    if not jti or not exp or not user_id:
        raise InvalidToken()

    now = datetime.now(timezone.utc).timestamp()

    remaining_seconds = int(exp - now)

#for blacklisting the token, we need to blacklist till it expires
#so from now(time),redis will have that token as blacklisted till token expires, once expiry done then token is removed from redis

    sid = payload.get("sid")
    if not sid:
        raise InvalidToken()

    await revoke_all_session_of_refresh_token(sid, session)
    await session.commit()  # remove all active tokens(jti)

    if remaining_seconds > 0:
        await add_to_blacklist_token(jti, remaining_seconds)

    return {"message": "logged out successfully ;)"}

async def request_account_deletion(user_id, session):

    user = await get_user_for_deletion_update(user_id, session)
    if not user:
        raise UserNotFound()

    if user.status == USER_STATUS_PURGING:
        raise UserPurgeInProgress()

    # if already pending deletion, just return existing state(no error)
    if user.status == USER_STATUS_PENDING_DELETION:
        return {
            "status": user.status,
            "deleted_at": user.deleted_at,
            "deletion_scheduled_for": user.deletion_scheduled_for,
            "restore_window_days": RESTORE_WINDOW_DAYS,
            "already_pending_deletion": True
        }

    result = await mark_user_pending_deletion(user=user, session=session)

    await create_user_deletion_audit_event(user_id=user.id, event_type="deleted_requested", session=session)

    await session.commit()

    return {
        "status": result["status"],
        "deleted_at": result["deleted_at"],
        "deletion_scheduled_for": result["deletion_scheduled_for"],
        "restore_window_days": RESTORE_WINDOW_DAYS,
        "already_pending_deletion": False
    }

async def account_restore(user_id, session):

    user = await get_user_for_deletion_update(
        user_id=user_id,
        session=session
    )

    if not user:
        raise UserNotFound()

    if user.status == USER_STATUS_PURGING:
        raise UserPurgeInProgress()

        # Idempotent restore:
        # if already restored to a live state, return success.
    if user.status in {"active", "suspended"}:
        return {
            "status": user.status,
            "restored": True,
            "already_restored": True
        }

    if user.status != USER_STATUS_PENDING_DELETION:
        raise InvalidAccountRestoreState()

    result = await restore_pending_deletion_user(
        user=user,
        session=session
    )

    await create_user_deletion_audit_event(
        user_id=user.id,
        event_type="restore_requested",
        session=session
    )

    await session.commit()

    return {
        "status": result["status"],
        "restored": True,
        "already_restored": False,
    }


