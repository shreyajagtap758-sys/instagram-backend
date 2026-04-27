"""bridge for deleted migration

Revision ID: f3d38d9ddcaa
Revises: None
"""
from alembic import op
import sqlalchemy as sa

# Is file ka ID wahi hona chahiye jo missing hai
revision = 'f3d38d9ddcaa'
down_revision = None # Agar ye sabse purani missing file hai

def upgrade():
    # Khali rakho, taaki DB mein kuch change na ho
    pass

def downgrade():
    # Khali rakho
    pass