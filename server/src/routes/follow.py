from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from server.src.core.db.database import get_session
from server.src.services.follow import (
    follow_user,
    unfollow_user,
    get_followers,
    get_following
)
from server.src.schemas.follow import (
    PaginationSchema,
    FollowResponse,
    FollowListResponse
)
from server.src.utils.dependency import get_current_user, get_current_user_optional


follow_router=APIRouter(prefix="/follow", tags=["follow"])


@follow_router.post("/{user_id}", response_model=FollowResponse)
async def follow(user_id : UUID, current_user = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    return await follow_user(current_user.id, user_id, session)

@follow_router.delete("/{user_id}", response_model=FollowResponse)
async def unfollow(user_id : UUID, current_user=Depends(get_current_user), session : AsyncSession=Depends(get_session)):
    return await unfollow_user(current_user.id, user_id, session)

@follow_router.get("/followers/{user_id}", response_model=FollowListResponse)
async def followers(user_id: UUID, viewer=Depends(get_current_user_optional), pagination: PaginationSchema = Depends(), session: AsyncSession = Depends(get_session)):
    return await get_followers(user_id=user_id, viewer=viewer, last_id=pagination.last_id, limit=pagination.limit, session=session)

@follow_router.get("/following/{user_id}", response_model=FollowListResponse)
async def following(user_id: UUID, viewer=Depends(get_current_user_optional), pagination: PaginationSchema = Depends(), session: AsyncSession = Depends(get_session)):
    return await get_following(user_id=user_id, viewer=viewer, last_id=pagination.last_id, limit=pagination.limit, session=session)



