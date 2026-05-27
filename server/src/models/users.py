from .base import Base


import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer, String, Boolean, func, text, Text, CheckConstraint, Index
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


UserStatus = {"active", "suspended"}


class User(Base):
    __tablename__= "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text('false')
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text('true')
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),  # Database level default
        nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True
    )
    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        default = False,
        server_default=text('false')
    )
    lock_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable = True
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text('false')
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default=text("'active'"),
        nullable=False,
        index=True
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    profile_picture_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    follower_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False
    )

    following_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False
    )
    multi_factor = relationship("MFA", back_populates="user", uselist=False) #uselist = one to one relation, ek user ka ek hi mfa record

    is_private: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False
    )

    liked_posts = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")


    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended')", name="valid_user_status"),
        CheckConstraint('follower_count >= 0', name='check_follower_count_positive'), #follower/following count must not go negative in db at any case
        CheckConstraint('following_count >= 0', name='check_following_count_positive'),
        Index("idx_active_users", "id", postgresql_where=(text("is_deleted = false"))), # db keep only those users who are not deleted
    )


