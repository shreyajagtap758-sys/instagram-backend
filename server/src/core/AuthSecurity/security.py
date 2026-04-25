import hashlib
from datetime import timedelta, timezone, datetime
from jose import jwt, JWTError
import uuid

from server.src.core.config import settings


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 5



with open(settings.PRIVATE_KEY_PATH, "r") as f:
    PRIVATE_KEY = f.read()

with open(settings.PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()

async def create_access_token(data:dict):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({"jti": str(uuid.uuid4()),"type": "access" ,"exp": expire})

    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return token

def create_refresh_token(user_id : str):
    jti = str(uuid.uuid4())
    exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "refresh",
        "exp": exp
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    return token, jti

async def hash_refresh_token(raw_refresh_token: str) -> str:
    return hashlib.sha256(raw_refresh_token.encode()).hexdigest()

async def decode_token(token: str):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

