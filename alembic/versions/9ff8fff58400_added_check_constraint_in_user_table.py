"""changed user_table a little

Revision ID: 9ff8fff58400
Revises: 96140bd2302b
Create Date: 2026-05-01 11:04:48.502470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ff8fff58400'
down_revision: Union[str, Sequence[str], None] = '96140bd2302b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        'check_follower_count_positive',
        'users',
        "follower_count >= 0"
    )
    op.create_check_constraint(
        'check_following_count_positive',
        'users',
        "following_count >= 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('check_follower_count_positive', 'users', type_='check')
    op.drop_constraint('check_following_count_positive', 'users', type_='check')
