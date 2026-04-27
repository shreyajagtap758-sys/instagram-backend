from server.src import models


from sqlalchemy import select


async def save_refresh_token(token: models.RefreshToken, session):
    session.add(token)
    await session.commit()
    await session.refresh(token)

    return token

async def get_refresh_token(token_hash: str, session):

    result = await session.execute(
        select(models.RefreshToken).where(
            models.RefreshToken.token_hash == token_hash
        )
    )

    return result.scalar_one_or_none()

