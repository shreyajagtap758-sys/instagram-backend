# db se baat krne wala folder

from server.src import models


from sqlalchemy import select, func, update


async def get_user_by_email(user_email, session):
    statement = select(models.User).where(models.User.email == user_email)
    result = await session.execute(statement)

    return result.scalar_one_or_none()

async def user_creation(new_user, session):
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

async def username_exists(username, session):
    result = await session.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalars().first()


async def get_user_by_id(user_id, session):
    result = await session.execute(select(models.User).where(models.User.id == user_id))

    return result.scalar_one_or_none()


async def get_active_sessions_count(user_id:str, session):
    result = await session.execute(
        select(func.count()).select_from(models.RefreshToken).
        where(models.RefreshToken.user_id == user_id,
              models.RefreshToken.revoked == False)
    )
    return result.scalar_one()

async def revoke_oldest_session(user_id: str, session):
    result = await session.execute(
        select(models.RefreshToken.id).
        where(models.RefreshToken.user_id == user_id,
        models.RefreshToken.revoked == False).
        order_by(models.RefreshToken.created_at.asc()).
        limit(1)
    )
    oldest = result.scalar_one_or_none()
    if oldest:
        await session.execute(
            update(models.RefreshToken)
            .where(models.RefreshToken.id == oldest)
            .values(revoked=True)
        )


