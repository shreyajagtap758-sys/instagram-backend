from datetime import datetime, timezone
from sqlalchemy import select, delete, update

from server.src import models
from server.src.repository.redis import invalidate_all_sessions


async def update_user_password(session, user_id: str, new_password_hash: str):

    await session.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(hashed_password=new_password_hash)
    )

    await session.commit()

async def save_reset_token(session, user_id: str, token_hash: str, expires_at: datetime):
    token = models.PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        used=False
    )
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token


async def get_reset_token_by_hash(token_hash: str, session):
    result = await session.execute(
        select(models.PasswordResetToken).where(
            models.PasswordResetToken.token_hash == token_hash
        )
    )
    return result.scalar_one_or_none()


async def mark_token_used(session, token_id: str):
    result = await session.execute(
        select(models.PasswordResetToken).where(
            models.PasswordResetToken.id == token_id
        )
    )
    token = result.scalar_one_or_none()

    if token:
        token.used = True
        await session.commit()


async def delete_expired_tokens(session):
    await session.execute(
        delete(models.PasswordResetToken).where(
            models.PasswordResetToken.expires_at < datetime.now(timezone.utc)
        )
    )
    await session.commit()




