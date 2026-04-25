# db se baat krne wala folder

from server.src import models


from sqlalchemy import select


async def get_user_by_email(user_email, session):
    statement = select(models.User).where(models.User.email == user_email)
    result = await session.execute(statement)

    return result.scalar_one_or_none()

async def user_creation(new_user, session):
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

async def get_user_by_id(user_id, session):
    result = await session.execute(select(models.User).where(models.User.id == user_id))

    return result.scalar_one_or_none()


