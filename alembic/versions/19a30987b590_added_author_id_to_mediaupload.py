"""added author id to mediaupload

Revision ID: 19a30987b590
Revises: d839994615c2
Create Date: 2026-05-19 11:32:45.551504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19a30987b590'
down_revision: Union[str, Sequence[str], None] = 'd839994615c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "media_uploads",
        "user_id",
        new_column_name="author_id"
    )

    op.drop_index(
        op.f("ix_media_uploads_user_id"),
        table_name="media_uploads"
    )

    op.create_index(
        op.f("ix_media_uploads_author_id"),
        "media_uploads",
        ["author_id"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_media_uploads_author_id"),
        table_name="media_uploads"
    )

    op.create_index(
        op.f("ix_media_uploads_user_id"),
        "media_uploads",
        ["user_id"],
        unique=False
    )

    op.alter_column(
        "media_uploads",
        "author_id",
        new_column_name="user_id"
    )
