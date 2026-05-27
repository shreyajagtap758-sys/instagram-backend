from .base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer, String, Boolean, func, text, Text, CheckConstraint, Index, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


from server.src.utils.enums import PostStatus, Visibility

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    caption: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    visibility: Mapped[str] = mapped_column(
        String,
        default = Visibility.PUBLIC,
        server_default=text("'public'"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=PostStatus.PUBLISHED,
        server_default=text("'published'"),
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

    media = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    

    __table_args__ = (
        CheckConstraint(
            "status IN ('published', 'deleted')",
            name="valid_post_status"
        ),
        CheckConstraint("visibility IN ('public', 'private')", name="valid_post_visibility"),
        Index("idx_post_user_created", "author_id", "created_at", "id"),
    )