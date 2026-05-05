from .base import Base


import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer, String, Boolean, func, text, Text, CheckConstraint, Index, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class post_media(Base):
    __tablename__ = "post_media"

    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    post_id : Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
        index=True
    )
    media_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )
    media_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    order_index : Mapped[int] = mapped_column(
        Integer
    )


    __table_args__ = (
        CheckConstraint(
            "media_type IN ('image', 'video', 'text')",
            name="valid_media_type"
        ),
    )
