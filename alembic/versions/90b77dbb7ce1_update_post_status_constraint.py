"""update post status constraint

Revision ID: 90b77dbb7ce1
Revises: 19a30987b590
Create Date: 2026-05-19 12:12:57.921166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90b77dbb7ce1'
down_revision: Union[str, Sequence[str], None] = '19a30987b590'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.drop_constraint(
        "valid_post_status",
        "posts",
        type_="check"
    )

    op.create_check_constraint(
        "valid_post_status",
        "posts",
        "status IN ('published', 'deleted')"
    )


def downgrade() -> None:

    op.drop_constraint(
        "valid_post_status",
        "posts",
        type_="check"
    )

    op.create_check_constraint(
        "valid_post_status",
        "posts",
        "status IN ('active', 'hidden', 'deleted')"
    )
