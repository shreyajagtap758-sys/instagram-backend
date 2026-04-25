# multi factor authentication = time based one time password

import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MFA(Base):
    __tablename__ = "mfa"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default = False
    )
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    user = relationship("User", back_populates="multi_factor")

