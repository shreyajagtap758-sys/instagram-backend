import uuid

from server.src.repository.redis import invalidate_all_sessions
from server.src.schemas.user import get_refresh_token
from server.src.core.AuthSecurity.security import create_access_token, create_refresh_token
from server.src.core.AuthSecurity.security import hash_refresh_token
from server.src.core.redis import redis_client
from server.src import models
from server.src.core.AuthSecurity.security import decode_token
from server.src.repository.user import get_active_sessions_count, revoke_oldest_session
from server.src.repository.token import save_refresh_token, get_refresh_token, revoke_refresh
from server.src.error_handling.exceptions.authExceptions import InvalidRefreshToken, UnauthorizedError, TooManyRequests
from server.src.utils.redis import check_refresh_rate_limit


from datetime import datetime, timedelta, timezone


REFRESH_TOKEN_EXPIRE_DAYS = 5
MAX_SESSIONS = 5


async def generate_tokens(user, session):
    now = datetime.now(timezone.utc)
    
    sid = str(uuid.uuid4())

    sessions = await get_active_sessions_count(str(user.id), session)

    if sessions >= MAX_SESSIONS:
        await revoke_oldest_session(str(user.id), session)

    # ACCESS TOKEN
    access_token, access_jti, access_exp = create_access_token({"sub": str(user.id), "email": user.email, "sid" : sid, "type": "access"}) # new session

    # REFRESH TOKEN
    raw_refresh, refresh_jti, refresh_exp = await create_refresh_token(str(user.id), sid)
    hashed_refresh = hash_refresh_token(raw_refresh)

    token_data = models.RefreshToken(
        id=refresh_jti,
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=refresh_exp,
        revoked=False,
        sid=sid,
        created_at=now
    )

    await save_refresh_token(token_data, session)

    return {"access_token": access_token,
            "refresh_token": raw_refresh}


async def rotate_refresh_token(old_refresh_token: str, session):
    payload = decode_token(old_refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise InvalidRefreshToken()

    allowed = await check_refresh_rate_limit(user_id=payload.get("sub"), redis_client=redis_client)

    if not allowed:
        raise TooManyRequests()

    hash_token = hash_refresh_token(old_refresh_token)

    db_token = await get_refresh_token(hash_token, session)

    if not db_token:
        raise InvalidRefreshToken()

    #expiry check first
    if db_token.expires_at < datetime.now(timezone.utc):
        raise InvalidRefreshToken()

    #pass one reuest at a time for revoking = true(if two comes at same time)
    revoked = await revoke_refresh(db_token.id, session)

    if not revoked:
        #reuse detected: kill all session
        await invalidate_all_sessions(db_token.user_id, session)
        await session.commit()
        raise UnauthorizedError()

    user_id = payload.get("sub")
    new_sid = payload.get("sid")

    new_access, new_access_jti, new_access_exp = create_access_token({"sub": user_id, "email": payload.get("email"), "sid": str(new_sid), "type": "access"})

    new_refresh_raw, new_refresh_jti, new_refresh_exp = await create_refresh_token(str(user_id), new_sid)
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

    return {
        "access_token": new_access,
        "refresh_token": new_refresh_raw
    }

