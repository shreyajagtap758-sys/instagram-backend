from typing import Optional

from pydantic import BaseModel, Field


class CreatePost(BaseModel):
    caption: Optional[str] = Field(None, max_length=1000)
    media_url: Optional[str] = Field(None, max_length=1000)
    media_type : str
    visibility: str = "public"