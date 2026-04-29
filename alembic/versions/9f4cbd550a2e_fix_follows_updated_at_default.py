"""fix_follows_updated_at_default

Revision ID: 9f4cbd550a2e
Revises: 8f1cb3893a82
Create Date: 2026-04-29 19:20:32.990596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f4cbd550a2e'
down_revision: Union[str, Sequence[str], None] = '8f1cb3893a82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQL command manually chala rahe hain taaki koi confusion na rahe
    op.execute("ALTER TABLE follows ALTER COLUMN updated_at SET DEFAULT now()")
    # Purane records mein agar NULL hai toh unhe bhi update kar dete hain
    op.execute("UPDATE follows SET updated_at = now() WHERE updated_at IS NULL")
    # Not null constraint ensure karo
    op.alter_column('follows', 'updated_at', nullable=False)


def downgrade() -> None:
    op.execute("ALTER TABLE follows ALTER COLUMN updated_at DROP DEFAULT")
    op.alter_column('follows', 'updated_at', nullable=True)
