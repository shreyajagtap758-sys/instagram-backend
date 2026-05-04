from datetime import datetime, timezone, timedelta
from sqlalchemy import select, delete, update, func

from server.src import models


async def update_user_password(session, user_id: str, new_password_hash: str):
    await session.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(hashed_password=new_password_hash)
    )


async def save_reset_token(session, user_id: str, token_hash: str, expires_at: datetime):
    token = models.PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        used=False
    )
    session.add(token)
    return token


async def get_reset_token_by_hash(token_hash: str, session):
    result = await session.execute(
        select(models.PasswordResetToken).where(
        models.PasswordResetToken.token_hash == token_hash
        )
    )
    return result.scalar_one_or_none()


async def mark_token_used(session, token_id):
    result = await session.execute(
        update(models.PasswordResetToken)
        .where(
            models.PasswordResetToken.id == token_id,
            models.PasswordResetToken.used == False
        )
        .values(used=True)
    )
    return result.rowcount == 1

async def mark_all_tokens_used_for_user(user_id, session):
    await session.execute(update(models.PasswordResetToken).
                          where(models.PasswordResetToken.user_id == user_id,
                                models.PasswordResetToken.used == False).
                          values(used=True)
                          )


async def delete_expired_tokens(session):
    await session.execute(
        delete(models.PasswordResetToken).where(
            models.PasswordResetToken.expires_at < datetime.now(timezone.utc)
        )
    )

async def user_fetched_tokens(session, user_id:str):
    result = await session.execute(
        select(func.count(models.PasswordResetToken.id)).
        where(models.PasswordResetToken.user_id == user_id,
              models.PasswordResetToken.created_at > datetime.now(timezone.utc) - timedelta(hours=1),
              models.PasswordResetToken.used == False
            )
        )

    return result.scalar()

async def invalidate_reset_token(user_id, session):
    await session.execute(update(models.PasswordResetToken).
                          where(models.PasswordResetToken.user_id == user_id,
                                models.PasswordResetToken.used == False).
                          values(used=True))
