from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from core.AuthSecurity.security import decode_token
from server.src.core.db.database import get_session
from server.src.schemas.user import UserCreate, UserResponse, UserLogin
from server.src.services.users import create_user, login_user
from server.src.utils.dependency import get_current_user
from server.src.services.tokens import rotate_refresh_token
from server.src.services.users import logout_user
from utils.dependency import oauth2_scheme

user_router = APIRouter()


@user_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session : AsyncSession = Depends(get_session)):
    return await create_user(user_data, session)

@user_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, session : AsyncSession = Depends(get_session)) -> dict:
    return await login_user(user_data, session)

@user_router.get("/me")
async def current_user(current = Depends(get_current_user)):
    return current

@user_router.post("/get_access_token")
async def refresh(refresh_token : str, session : AsyncSession = Depends(get_session)) -> dict:
    return await rotate_refresh_token(refresh_token, session)

@user_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    payload = await decode_token(token)
    if not payload:
        return {"error": "invalid token"}

    return await logout_user(payload)

