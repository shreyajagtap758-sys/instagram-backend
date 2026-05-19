import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, String, ForeignKey, CheckConstraint, Index
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column


from .base import Base
from server.src.utils.enums import UploadStatus

class MediaUpload(Base):
    __tablename__ = "media_uploads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    author_id : Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    object_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )
    media_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=UploadStatus.PENDING,
        server_default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'attached')",
            name="valid_upload_status"
        ),
        Index("idx_upload_status_created", "status", "created_at"),
    )




