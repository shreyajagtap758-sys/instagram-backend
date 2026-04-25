from datetime import datetime, timedelta, timezone


from server.src.repository.user import get_user_by_email, user_creation
from server.src.core.AuthSecurity.auth import verify_password, hash_password
from server.src import models
from server.src.services.tokens import generate_tokens

MAX_FAILED_ATTEMPTS = 5
LOCK_UNTIL_MINUTES = 15

async def create_user(user_data, session):
    existing = await get_user_by_email(user_data.email, session)
    if existing:
        raise ValueError("email already exists")

    user = models.User(email = user_data.email,username=user_data.username,hashed_password = hash_password(user_data.password))

    return await user_creation(user, session)


async def login_user(user_data, session):
    user = await get_user_by_email(user_data.email, session)

    if not user:
        raise ValueError("user does not exist/invalid credentials")

    if user.is_locked and user.lock_until and user.lock_until > datetime.utcnow():
        raise ValueError("sorry, too many attempts. Account temporarily locked")

    if user.is_locked and user.lock_until and user.lock_until <= datetime.utcnow():
        user.is_locked = False
        user.lock_until = None
        user.failed_login_attempts = 0
        await session.commit()

    if not verify_password(user_data.password, user.hashed_password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.is_locked = True
            user.lock_until = datetime.utcnow() + timedelta(minutes=LOCK_UNTIL_MINUTES)

        await session.commit()

        return {"error": "invalid credentials"}

    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    await session.commit()

    return await generate_tokens(user, session)


