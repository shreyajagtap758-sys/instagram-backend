from .base import Base


import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer, String, Boolean, func, text, Text, CheckConstraint, Index, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


PostStatus = {"active", "hidden", "deleted"}


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    caption: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default=text("'active'"),
        nullable=False,
        index=True
    )

    like_count: Mapped[int] = mapped_column(
        default=0,
        server_default=text("0"),
        nullable=False
    )

    comment_count: Mapped[int] = mapped_column(
        default=0,
        server_default=text("0"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'hidden', 'deleted')",
            name="valid_post_status"
        ),
        Index("idx_post_user", "user_id"),
        Index("idx_post_status", "status"),
    )