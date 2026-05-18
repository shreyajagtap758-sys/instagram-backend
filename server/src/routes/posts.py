from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.src.schemas.post import CreatePost, PaginationSchema, UploadUrlRequest, UpdatePost
from server.src.utils.dependency import get_current_user, get_current_user_optional
from server.src.core.db.database import get_session
from services.post_service.post import post_creation, post_delete, post_get, user_posts, upload_url_generation, post_update

post_router = APIRouter(prefix="/post", tags=["post"])


@post_router.post("/create_post")
async def create_post(data: CreatePost, current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await post_creation(current_user.id, data, session)

@post_router.get("/get_post/{post_id}")
async def get_post(post_id: str, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await post_get(post_id, user, session)

@post_router.delete("/delete_post/{post_id}")
async def delete_post(post_id: str, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await post_delete(post_id, user.id, session)

@post_router.get("/get_user_post/{user_id}")
async def get_user_post(user_id: str, pagination : PaginationSchema = Depends(), user = Depends(get_current_user_optional), session : AsyncSession = Depends(get_session)):
    return await user_posts(user_id= user_id, pagination=pagination, user=user, session=session)

@post_router.post("/media/upload-url")
async def generate_upload_url(data: UploadUrlRequest, user = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    return await upload_url_generation(data, user.id, session)

@post_router.patch("/update_post/{post_id}")
async def update_post(post_id: str, data: UpdatePost, user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await post_update(post_id=post_id, data=data, user_id=str(user.id), session=session)
