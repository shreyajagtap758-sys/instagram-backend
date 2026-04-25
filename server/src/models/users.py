from .base import Base


import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer, String, Boolean, func
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
        default=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
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
        String(100),
        nullable=False
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True
    )
    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        default = False
    )
    lock_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable = True
    )

    multi_factor = relationship("MFA", back_populates="user", uselist=False) #uselist = one to one relation, ek user ka ek hi mfa record

