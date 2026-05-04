from server.src import models


from sqlalchemy import select, update


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


async def revoke_all_session_of_refresh_token(sid: str, session):
    await session.execute(
        update(models.RefreshToken)
        .where(models.RefreshToken.sid == sid)
        .values(revoked=True)
    )

async def revoke_refresh(token_id:str, session):
    result = await session.execute(update(models.RefreshToken).
                                   where(models.RefreshToken.id == token_id,
                                   models.RefreshToken.revoked == False).
                                   values(revoked=True))
    return result.rowcount == 1
