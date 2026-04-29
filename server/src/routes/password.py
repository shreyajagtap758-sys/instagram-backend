from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.src.schemas.password import ChangePassword, ForgotPassword, ResetPassword
from server.src.utils.dependency import get_current_user
from server.src.services.password import change_password, forgot_password, reset_password
from server.src.core.db.database import get_session


password_router = APIRouter(prefix="/password", tags=["password"])


@password_router.post("/change-password")
async def change_pass(data: ChangePassword, user = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    return await change_password(user, data, session)

@password_router.post("/forgot-password")
async def forgot_password_route(data: ForgotPassword, session : AsyncSession = Depends(get_session)):
    return await forgot_password(data, session)


@password_router.post("/reset-password")
async def reset_password_route(data: ResetPassword, session : AsyncSession = Depends(get_session)):
    return await reset_password(data, session)


