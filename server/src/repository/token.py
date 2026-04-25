from server.src import models


from sqlalchemy import select


async def save_token(token: models.RefreshToken, session):
    session.add(token)
    await session.commit()
    await session.refresh(token)

    return token

async def get_by_token_hash(token_hash: str, session):
    result = await session.execute(select(models.RefreshToken).where(models.RefreshToken.token_hash == token_hash))

    return result.scalar_one_or_none()

