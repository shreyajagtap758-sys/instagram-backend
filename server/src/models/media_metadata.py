from .base import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer, String, Boolean, func, text, Text, CheckConstraint, Index, ForeignKey, \
    UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PostMedia(Base):
    __tablename__ = "post_media"

    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    post_id : Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    object_key: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
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
        Integer,
        nullable=False
    )
    post = relationship(
        "Post",
        back_populates="media"
    )


    __table_args__ = (
        CheckConstraint(
            "media_type IN ('image', 'video')",
            name="valid_media_type"
        ),
        CheckConstraint("order_index >= 0", name="valid_order_index"),
        UniqueConstraint("post_id", "order_index", name="uq_post_media_order"),
        Index("idx_post_media_post_order", "post_id", "order_index"),
    )
