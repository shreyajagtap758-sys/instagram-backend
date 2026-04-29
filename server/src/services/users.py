from datetime import datetime, timedelta, timezone


from server.src.repository.redis import remove_active_tokens
from server.src.error_handling.exceptions.authExceptions import InvalidToken, TokenExpired
from server.src.error_handling.exceptions.authExceptions import InvalidCredentials
from server.src.repository.redis import add_to_blacklist_token
from server.src.repository.user import get_user_by_email, user_creation, username_exists
from server.src.core.AuthSecurity.auth import verify_password, hash_password
from server.src import models
from server.src.services.tokens import generate_tokens
from server.src.error_handling.exceptions.userExceptions import EmailAlreadyExists, UsernameNotValid
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


async def login_user(user_data, session):
    email = normalize_email(user_data.email)

    user = await get_user_by_email(email, session)

    if not user:
        raise InvalidCredentials()

    if user.is_locked and user.lock_until and user.lock_until > datetime.now(timezone.utc):
        raise TooManyAttempts()

    if user.is_locked and user.lock_until and user.lock_until <= datetime.now(timezone.utc):
        user.is_locked = False
        user.lock_until = None
        user.failed_login_attempts = 0
        await session.commit()

    if not verify_password(user_data.password, user.hashed_password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.is_locked = True
            user.lock_until = datetime.now(timezone.utc) + timedelta(minutes=LOCK_UNTIL_MINUTES)

        await session.commit()

        raise InvalidCredentials()

    user.failed_login_attempts = 0
    user.last_login = datetime.now(timezone.utc)
    await session.commit()

    return await generate_tokens(user, session)



async def logout_user(payload: dict):
    jti = payload.get("jti")
    exp = payload.get("exp")
    user_id = payload.get("sub")

    if not jti or not exp or not user_id:
        return InvalidToken()

    now = datetime.now(timezone.utc).timestamp()

    remaining_seconds = int(exp - now)

#for blacklisting the token, we need to blacklist till it expires
#so from now(time),redis will have that token as blacklisted till token expires, once expiry done then token is removed from redis

    if remaining_seconds <= 0:  # token expired, so remaining sec 0 now
        return TokenExpired()

    await add_to_blacklist_token(jti, remaining_seconds)

    await remove_active_tokens(user_id, jti)  # remove all active tokens(jti)

    return {"message": "logged out successfully ;)"}

