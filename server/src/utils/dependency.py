from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.requests import Request


from server.src.core.db.database import get_session
from server.src.core.AuthSecurity.security import decode_token
from server.src.repository.user import get_user_by_id
from server.src.repository.redis import is_blacklisted
from server.src.error_handling.exceptions.authExceptions import (InvalidToken,UnauthorizedError)
from server.src.error_handling.exceptions.userExceptions import UserNotFound


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    payload = decode_token(token)

    if not payload:
        raise InvalidToken()

    jti = payload.get("jti")

    if not jti:
        raise UnauthorizedError()

    if await is_blacklisted(jti):
        raise UnauthorizedError()


    user_id = payload.get("sub")
    if not user_id:
        print(f"DEBUG: Payload content is -> {payload}")
        raise UnauthorizedError()

    user = await get_user_by_id(user_id, session)

    if not user:
        raise UserNotFound()

    return user

async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    try:
        return await get_current_user(
            request=request,
            session=session
        )

    except JWTError:
        return None

    except Exception:
        return None