async def check_refresh_rate_limit(user_id: str, redis_client, limit: int = 5, window: int = 60):
    key = f"refresh_limit:{user_id}"

    count = await redis_client.incr(key)

    if count == 1:
        await redis_client.expire(key, window)

    if count > limit:
        return False

    return True