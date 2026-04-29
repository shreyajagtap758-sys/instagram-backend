"""added some changes to follow, user table

Revision ID: 8f1cb3893a82
Revises: 738447014994
Create Date: 2026-04-29 18:57:16.605785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f1cb3893a82'
down_revision: Union[str, Sequence[str], None] = '738447014994'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Hashed Password length update
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.VARCHAR(length=100),
                    type_=sa.String(length=255),
                    existing_nullable=False)

    # 2. User table ke defaults aur constraints fix karo
    op.alter_column('users', 'failed_login_attempts',
                    server_default=sa.text('0'),
                    existing_nullable=False)

    op.create_index('idx_active_users', 'users', ['id'],
                    unique=False, postgres_where=sa.text('is_deleted = false'))

    op.create_check_constraint(
        'valid_user_status',
        'users',
        "status IN ('active', 'disabled', 'deleted')"
    )

    # 3. Follow table ke updated_at aur status constraints fix karo
    op.alter_column('follows', 'updated_at',
                    existing_type=sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False)

    op.create_check_constraint(
        'valid_follow_status',
        'follows',
        "status IN ('active', 'blocked', 'pending')"
    )


def downgrade() -> None:
    # Constraints drop karo
    op.drop_constraint('valid_follow_status', 'follows', type_='check')
    op.drop_constraint('valid_user_status', 'users', type_='check')

    # Defaults revert karo
    op.alter_column('follows', 'updated_at',
                    server_default=None,
                    nullable=True)

    op.alter_column('users', 'failed_login_attempts',
                    server_default=None)

    # Index aur Password length revert karo
    op.drop_index('idx_active_users', table_name='users', postgres_where=sa.text('is_deleted = false'))
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(length=255),
                    type_=sa.VARCHAR(length=100),
                    existing_nullable=False)