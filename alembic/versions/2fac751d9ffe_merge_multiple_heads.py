"""merge_multiple_heads

Revision ID: 2fac751d9ffe
Revises: 769ed5c014c6, eb7b08a20352
Create Date: 2026-04-26 20:46:18.107441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fac751d9ffe'
down_revision: Union[str, Sequence[str], None] = ('769ed5c014c6', 'eb7b08a20352')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
