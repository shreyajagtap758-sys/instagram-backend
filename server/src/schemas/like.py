from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class LikeCursorPagination(BaseModel):
    limit: int = Field(default=20, ge=1, le=30)
    snapshot_time: datetime
    last_created_at: datetime | None = None
    last_id: UUID | None = None


class LikeResponse(BaseModel):
    liked: bool
    like_count: int


class PostLikeUserResponse(BaseModel):
    user_id: UUID
    username: str
    profile_picture_url: str | None
    liked_at: datetime


class UserLikedPostResponse(BaseModel):
    post_id: UUID
    caption: str | None
    liked_at: datetime