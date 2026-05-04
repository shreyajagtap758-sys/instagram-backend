from server.src.core.redis import redis_client
from server.src import models

BLACKLIST_KEY = "blacklist:{}"

async def add_to_blacklist_token(jti:str, expire_seconds: int):
    if not jti or expire_seconds <= 0:
        return
    await redis_client.setex(
        BLACKLIST_KEY.format(jti),
        expire_seconds,
        "1"
    )

async def is_blacklisted(jti: str) -> bool:
    if not jti:
        return False

    return await redis_client.exists(
        BLACKLIST_KEY.format(jti)
    ) == 1


from sqlalchemy import update

async def invalidate_all_sessions(user_id: str, session):
    await session.execute(
        update(models.RefreshToken)
        .where(models.RefreshToken.user_id == user_id)
        .values(revoked=True)
    )


