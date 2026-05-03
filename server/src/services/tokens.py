import uuid

from server.src.schemas.user import get_refresh_token
from server.src.core.AuthSecurity.security import create_access_token, create_refresh_token
from server.src.core.AuthSecurity.security import hash_refresh_token
from server.src import models
from server.src.core.AuthSecurity.security import decode_token
from server.src.repository.password import get_reset_token_by_hash
from server.src.repository.token import save_refresh_token, get_refresh_token
from server.src.error_handling.exceptions.authExceptions import InvalidRefreshToken, UnauthorizedError
from server.src.repository.redis import store_active_token
from server.src.core.redis import redis_client


from datetime import datetime, timedelta, timezone

REFRESH_TOKEN_EXPIRE_DAYS = 5


async def generate_tokens(user, session):
    now = datetime.now(timezone.utc)

    sid = str(uuid.uuid4())

    # ACCESS TOKEN
    access_token, access_jti, access_exp = create_access_token({"sub": str(user.id), "email": user.email, "sid" : sid, "type": "access"}) # new session

    access_ttl = int((access_exp - now).total_seconds())

    # REFRESH TOKEN
    raw_refresh, refresh_jti, refresh_exp = await create_refresh_token(str(user.id))
    hashed_refresh = hash_refresh_token(raw_refresh)


    token_data = models.RefreshToken(
        id=refresh_jti,
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=refresh_exp,
        revoked=False,
        sid=sid
    )

    await save_refresh_token(token_data, session)

    refresh_ttl = int((refresh_exp - now).total_seconds())

    await store_active_token(str(user.id), access_jti, access_ttl)
    await store_active_token(str(user.id), refresh_jti, refresh_ttl)

    pipe = redis_client.pipeline()

    pipe.sadd(f"active_access:{user.id}", access_jti)
    pipe.sadd(f"active_refresh:{user.id}", refresh_jti)

    pipe.expire(f"active_access:{user.id}", access_ttl)
    pipe.expire(f"active_refresh:{user.id}", refresh_ttl)

    await pipe.execute()

    return {"access_token": access_token,
            "refresh_token": raw_refresh}


async def rotate_refresh_token(old_refresh_token: str, session):
    payload = decode_token(old_refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise InvalidRefreshToken()

    hash_token = hash_refresh_token(old_refresh_token)

    db_token = await get_refresh_token(hash_token, session)

    if not db_token:
        raise InvalidRefreshToken()

    if db_token.revoked:
        raise UnauthorizedError()

    if db_token.expires_at < datetime.now(timezone.utc):
        raise InvalidRefreshToken()

    db_token.revoked = True
    await session.commit()

    # blacklist old jti (IMPORTANT FIX)
    await redis_client.setex(
        f"blacklist:{db_token.id}",
        86400,
        "1"
    )

    user_id = payload.get("sub")
    new_sid = db_token.sid

    new_access, new_access_jti, new_access_exp = create_access_token({"sub": user_id, "email": payload.get("email"), "sid": str(new_sid), "type": "access"})

    new_refresh_raw, new_refresh_jti, new_refresh_exp = await create_refresh_token(str(user_id))
    new_refresh_hashed = hash_refresh_token(new_refresh_raw)

    new_refresh_store = models.RefreshToken(
        id=new_refresh_jti,
        user_id=user_id,
        token_hash=new_refresh_hashed,
        expires_at=new_refresh_exp,
        revoked=False,
        sid=new_sid
    )
    await save_refresh_token(new_refresh_store, session)
    await session.commit()

    now = datetime.now(timezone.utc)

    access_ttl = int((new_access_exp - now).total_seconds())
    refresh_ttl = int((new_refresh_exp - now).total_seconds())

    pipe = redis_client.pipeline()

    pipe.sadd(f"active_access:{user_id}", new_access_jti)
    pipe.sadd(f"active_refresh:{user_id}", new_refresh_jti)

    pipe.expire(f"active_access:{user_id}", access_ttl)
    pipe.expire(f"active_refresh:{user_id}", refresh_ttl)

    await pipe.execute()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh_raw
    }

