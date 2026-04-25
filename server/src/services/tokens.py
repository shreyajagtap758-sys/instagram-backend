from server.src.core.AuthSecurity.security import create_access_token, create_refresh_token
from server.src.core.AuthSecurity.security import hash_refresh_token
from server.src import models
from server.src.core.AuthSecurity.security import decode_token
from server.src.repository.token import get_by_token_hash, save_token


import uuid
from jose import JWTError
from datetime import datetime, timedelta


REFRESH_TOKEN_EXPIRE_DAYS = 5

async def generate_tokens(user, session):
    # ACCESS TOKEN
    access_token = await create_access_token({"user_id": str(user.id), "email": user.email})

    # REFRESH TOKEN
    raw_refresh = create_refresh_token()
    hashed_refresh = await hash_refresh_token(raw_refresh)
    expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    token_data = models.RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=expiry,
        revoked=False
    )

    await save_token(token_data, session)

    return {"access_token": access_token,
            "refresh_token": raw_refresh}


async def rotate_refresh_token(old_refresh_token : str, session):
    payload = await decode_token(old_refresh_token)

    hash_token = await hash_refresh_token(old_refresh_token)

    db_token = await get_by_token_hash(hash_token, session)

    if not db_token:
        raise ValueError("invalid refresh token, please provide refresh token here")

    if db_token.revoked:
        raise ValueError("token used")

    if db_token.expires_at < datetime.utcnow():
        raise ValueError("refresh token expired")

    db_token.revoked=True
    await session.commit()

    user_id = payload.get("user_id")

    new_access = await create_access_token({"user_id": user_id})

    new_refresh_raw = create_refresh_token()
    new_refresh_hashed = await hash_refresh_token(new_refresh_raw)

    new_refresh_store = models.RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=new_refresh_hashed,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False
    )
    await save_token(new_refresh_store, session)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh_raw
    }

