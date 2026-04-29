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


from datetime import datetime, timedelta, timezone

REFRESH_TOKEN_EXPIRE_DAYS = 5


async def generate_tokens(user, session):
    now = datetime.now(timezone.utc)

    # ACCESS TOKEN
    access_token, access_jti, access_sid, access_exp = create_access_token({"sub": str(user.id), "email": user.email, "sid" : str(uuid.uuid4())}) # new session

    access_ttl = int((access_exp - now).total_seconds())

    # REFRESH TOKEN
    raw_refresh, refresh_jti, refresh_exp = create_refresh_token(str(user.id))
    hashed_refresh = hash_refresh_token(raw_refresh)
    expiry = refresh_exp


    token_data = models.RefreshToken(
        id=refresh_jti,
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=expiry,
        revoked=False
    )

    await save_refresh_token(token_data, session)

    refresh_ttl = int((refresh_exp - now).total_seconds())

    await store_active_token(str(user.id), access_jti, access_ttl)
    await store_active_token(str(user.id), refresh_jti, refresh_ttl)


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

    db_token.revoked=True
    await session.commit()

    user_id = payload.get("sub")
    new_jti = payload.get("jti")

    new_access = create_access_token({"sub": user_id})

    new_refresh_raw, new_jti = create_refresh_token(user_id)
    new_refresh_hashed = hash_refresh_token(new_refresh_raw)

    new_refresh_store = models.RefreshToken(
        id=new_jti,
        user_id=user_id,
        token_hash=new_refresh_hashed,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False
    )
    await save_refresh_token(new_refresh_store, session)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh_raw
    }

