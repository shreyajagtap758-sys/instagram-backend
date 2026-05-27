from .base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, func, Index, ForeignKey, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PostLike(Base):
    __tablename__ = "post_likes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key = True,
        default=uuid.uuid4
    )

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User", back_populates="liked_posts")

    post = relationship("Post", back_populates="likes")

    __table_args__ = (
        # prevents duplicate likes
        UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_post_like_post_user"
        ),
        # efficient post likes queries
        Index(
            "idx_post_likes_post_created",
            "post_id",
            "created_at"
        ),
        # efficient user activity queries
        Index(
            "idx_post_likes_user_created",
            "user_id",
            "created_at"
        ),
    )


