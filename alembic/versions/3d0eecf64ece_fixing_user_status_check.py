"""fixing user status check

Revision ID: 3d0eecf64ece
Revises: c26db0cada3b
Create Date: 2026-07-13 13:44:58.951791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d0eecf64ece'
down_revision: Union[str, Sequence[str], None] = 'c26db0cada3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint(
        "valid_user_status",
        "users",
        type_="check"
    )

    op.create_check_constraint(
        "valid_user_status",
        "users",
        "status IN ('active', 'suspended', 'pending_deletion', 'purging')"
    )


def downgrade():
    op.drop_constraint(
        "valid_user_status",
        "users",
        type_="check"
    )

    op.create_check_constraint(
        "valid_user_status",
        "users",
        "status IN ('active', 'disabled', 'deleted')"
    )