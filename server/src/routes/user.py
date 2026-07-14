from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from server.src.core.AuthSecurity.security import decode_token
from server.src.core.db.database import get_session
from server.src.schemas.user import UserCreate, UserResponse, UserLogin, get_refresh_token, delete_account, restore_account
from server.src.services.users import create_user, login_user, request_account_deletion, account_restore
from server.src.utils.dependency import get_current_user
from server.src.services.tokens import rotate_refresh_token
from server.src.services.users import logout_user
from server.src.utils.dependency import oauth2_scheme

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session : AsyncSession = Depends(get_session)):
    return await create_user(user_data, session)

@user_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, session : AsyncSession = Depends(get_session)) -> dict:
    return await login_user(user_data, session)

@user_router.get("/me", response_model=UserResponse)
async def current_user(current = Depends(get_current_user)):
    return current

@user_router.post("/get_access_token")
async def get_new_access_token(data : get_refresh_token, session : AsyncSession = Depends(get_session)) -> dict:
    refresh_token = data.refresh
    return await rotate_refresh_token(refresh_token, session)

@user_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), session : AsyncSession = Depends(get_session)):
    payload = decode_token(token)
    if not payload:
        return {"error": "invalid token"}

    return await logout_user(payload, session)

@user_router.delete("/me/delete", response_model=delete_account)
async def delete_my_account(current = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    return await request_account_deletion(user_id=current.id, session=session)

@user_router.post("/me/restore", response_model=restore_account)
async def restore_my_account(current = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await account_restore(user_id=current.id, session=session)


