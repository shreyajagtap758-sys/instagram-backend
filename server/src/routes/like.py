from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from server.src.core.db.database import get_session
from server.src.utils.dependency import get_current_user
from server.src.schemas.like import LikeCursorPagination
from server.src.services.likes import (
    like_a_post,
    unlike_a_post,
    get_liked_post_users,
    get_user_liked_posts
)


like_router = APIRouter(prefix="/like", tags=["post_likes"])


@like_router.post("/{post_id}", status_code=status.HTTP_200_OK)
async def like_post(post_id: UUID, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await like_a_post(post_id=post_id, user_id=current_user.id, session=session)

@like_router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def unlike_post(post_id: UUID, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await unlike_a_post(post_id=post_id, user_id=current_user.id, session=session)

@like_router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def liked_post_all_users(post_id: UUID, pagination: LikeCursorPagination = Depends(), session: AsyncSession = Depends(get_session)):
    return await get_liked_post_users(post_id=post_id, pagination=pagination, session=session)

@like_router.get("/{user_id}/liked-posts", status_code=status.HTTP_200_OK)
async def get_user_liked_posts(user_id: UUID, pagination: LikeCursorPagination = Depends(), session: AsyncSession = Depends(get_session)):
    return await get_liked_post_users(user_id=user_id, pagination=pagination, session=session)

