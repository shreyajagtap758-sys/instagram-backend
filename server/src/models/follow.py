from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


from server.src.models.base import Base


FOLLOW_STATUS = {"active", "blocked", "pending"}


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    follower_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    following_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default=text("'active'"),
        nullable=False,
        index=True
    )

    is_muted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False
    )

    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    sid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )

    __table_args__ = (
        Index('ix_follows_following_created_follower', 'following_id', 'created_at', 'follower_id'),
        Index('ix_follows_follower_created_following', 'follower_id', 'created_at', 'following_id'),
        UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"), # one user can follow another only once.
        CheckConstraint("follower_id != following_id", name="no_self_follow"),  # avoid self follow
        CheckConstraint("status IN ('active', 'blocked', 'pending')", name="valid_follow_status"),
    )



