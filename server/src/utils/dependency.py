from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException


from server.src.core.db.database import get_session
from server.src.core.AuthSecurity.security import decode_token
from server.src.repository.user import get_user_by_id
from server.src.repository.redis import is_blacklisted


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    payload = await decode_token(token)

    if not payload:
        raise HTTPException(401, "Invalid token")

    jti = payload.get("jti")

    if await is_blacklisted(jti):
        raise HTTPException(401, "Token revoked")

    user_id = payload.get("sub")
    if not user_id:
        print(f"DEBUG: Payload content is -> {payload}")
        raise ValueError("token payload missing")

    user = await get_user_by_id(user_id, session)

    if not user:
        raise HTTPException(404, "User not found")

    return user