import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from typing import Optional


class PaginationSchema(BaseModel):
    last_created_at: Optional[datetime] = None
    last_id: Optional[UUID] = None
    limit: int = 20
    snapshot_time: Optional[datetime] = None

class PaginationCursor(BaseModel):
    last_created_at: Optional[datetime]
    last_id: Optional[UUID]
    snapshot_time: Optional[datetime]

class FollowResponse(BaseModel):
    status: str

class FollowListResponse(BaseModel):
    data: list[UUID]
    next_cursor: Optional[PaginationCursor]

