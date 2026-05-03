from server.src.core.redis import redis_client


async def add_to_blacklist_token(jti:str, expire_seconds: int):
    if expire_seconds <= 0:
        return
    await redis_client.setex(
        f"blacklist:{jti}",
        expire_seconds,
        "true"
    )

async def is_blacklisted(jti:str):
    result = await redis_client.get(f"blacklist:{jti}")
    return result is not None

async def store_active_token(user_id : str, jti : str, expire_seconds: int):
    if expire_seconds <= 0:
        return

    key = f"active_tokens:{user_id}"

    pipe = redis_client.pipeline()
    pipe.sadd(key, jti)
    pipe.expire(key, expire_seconds)

    await pipe.execute()

async def remove_active_tokens(user_id : str, jti: str):
    await redis_client.srem(f"active_tokens:{user_id}", jti)


async def invalidate_all_sessions(user_id: str, default_ttl: int = 86400):
    key = f"active_tokens:{user_id}"

    jtis = await redis_client.smembers(key)

    if not jtis:
        return

    pipe = redis_client.pipeline()

    for jti in jtis:
        pipe.setex(f"blacklist:{jti}", default_ttl, "1")

    pipe.delete(key)

    await pipe.execute()


