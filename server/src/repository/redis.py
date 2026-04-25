from server.src.core.redis import redis_client


async def add_to_blacklist_token(jti:str, expire_seconds: int):
    await redis_client.setex(
        f"blacklist:{jti}",
        expire_seconds,
        "true"
    )

async def is_blacklisted(jti:str):
    result = await redis_client.get(f"blacklist:{jti}")
    return result is not None


