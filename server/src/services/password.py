from datetime import datetime, timedelta, timezone

from passlib.exc import UsedTokenError


from server.src.repository.redis import invalidate_all_sessions
from server.src.error_handling.exceptions.userExceptions import UserNotFound
from server.src.core.AuthSecurity.auth import hash_password, verify_password
from server.src.error_handling.exceptions.authExceptions import InvalidCredentials, TokenExpired, InvalidToken
from server.src.utils.validations import validate_password, normalize_email
from server.src.repository.password import update_user_password, get_reset_token_by_hash, mark_token_used_and_delete, user_fetched_tokens
from server.src.repository.user import get_user_by_email, get_user_by_id
from server.src.error_handling.exceptions.securityExceptions import SamePass
from server.src.utils.tokens import generate_raw_token, hash_token
from server.src.repository.password import save_reset_token
from server.src.utils.tokens import send_reset_email


async def change_password(user, data, session):

    try:
        if not verify_password(data.old_password, user.hashed_password):
            raise InvalidCredentials()

        if data.old_password == data.new_password:
            raise SamePass()

        new_pass = validate_password(data.new_password)

        new_hash = hash_password(new_pass)

        await update_user_password(session, user.id, new_hash)

        await invalidate_all_sessions(str(user.id))
        await session.commit()

        return {"message": "Password changed successfully"}

    except Exception as e:
        await session.rollback()
        raise e


async def forgot_password(data, session):
    try:
        email = normalize_email(data.email)

        user = await get_user_by_email(email, session)

        if not user:
            return {"message": "If email exists, reset link has been sent"}

        recent_tokens = await user_fetched_tokens(session, user.id)
        if recent_tokens >= 3:
            return {"message": "If email exists, reset link has been sent"}

        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        await save_reset_token(
            session,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        await send_reset_email(user.email, raw_token)
        await session.commit()

        return {"message": "If email exists, reset link has been sent"}

    except Exception as e:
        await session.rollback()
        raise e


async def reset_password(data, session):

    try:
        if not data.token or len(data.token) < 10:
            raise Exception("Invalid token format")

        # 1. hash incoming token
        token_hash = hash_token(data.token)

        # 2. fetch token record
        record = await get_reset_token_by_hash(token_hash, session)

        # 3. validate token existence
        if not record:
            raise InvalidToken()

        # 4. check if already used
        if record.used:
            raise UsedTokenError()

        # 5. check expiry
        if record.expires_at < datetime.now(timezone.utc):
            raise TokenExpired()

        # 6. get user
        user = await get_user_by_id(session, record.user_id)

        if not user:
            raise UserNotFound()

        new_pass = validate_password(data.new_password)

        # 7. hash new password
        new_hash = hash_password(new_pass)

        # 8. update password
        await update_user_password(session, user.id, new_hash)

        await mark_token_used_and_delete(session, record.id)

        await invalidate_all_sessions(str(user.id))
        await session.commit()

        return {"message": "Password reset successful"}

    except Exception as e:
        await session.rollback()
        raise e



