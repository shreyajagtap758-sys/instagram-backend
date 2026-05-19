from server.src.core.redis import redis_client

UPLOAD_URL_WINDOW_SECONDS = 1200

async def check_upload_rate_limit(user_id: str):
    key = f"upload_rate_limit:{user_id}"

    current = await redis_client.incr(key)

    if current == 1:
        await redis_client.expire(key, UPLOAD_URL_WINDOW_SECONDS)

    ttl = await redis_client.ttl(key)

    return current, ttl