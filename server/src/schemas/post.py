from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class MediaInput(BaseModel):
    media_url: str
    media_type: str


class CreatePost(BaseModel):
    caption: Optional[str] = Field(None, max_length=1000)
    media: List[MediaInput] = Field(default_factory=list)
    visibility: str = "public"


class PaginationSchema(BaseModel):
    last_created_at: Optional[datetime] = None
    last_id: Optional[UUID] = None
    limit: int = Field(default=20, ge=1, le=20)
    snapshot_time: Optional[datetime] = None

class PaginationCursor(BaseModel):
    next_created_at: Optional[datetime] = None
    next_id: Optional[UUID] = None
    snapshot_time: Optional[datetime] = None
