from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


from server.src.utils.enums import Visibility, MediaType

class MediaInput(BaseModel):
    object_key: str
    media_type: MediaType


class CreatePost(BaseModel):
    caption: Optional[str] = Field(None, max_length=1000)
    media: List[MediaInput] = Field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC


class PaginationSchema(BaseModel):
    last_created_at: Optional[datetime] = None
    last_id: Optional[UUID] = None
    limit: int = Field(default=20, ge=1, le=20)
    snapshot_time: Optional[datetime] = None

class PaginationCursor(BaseModel):
    next_created_at: Optional[datetime] = None
    next_id: Optional[UUID] = None
    snapshot_time: Optional[datetime] = None


class UploadUrlRequest(BaseModel):
    media_type: MediaType
    file_size: int

class UploadUrlResponse(BaseModel):
    upload_url: str
    object_key: str


class UpdatePost(BaseModel):
    caption: Optional[str] = Field(None, max_length=1000)
    visibility: Optional[Visibility] = None
