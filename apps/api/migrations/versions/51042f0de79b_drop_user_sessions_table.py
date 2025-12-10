"""drop_user_sessions_table

Revision ID: 51042f0de79b
Revises: 301576e22585
Create Date: 2025-12-10 22:49:57.094333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51042f0de79b'
down_revision: Union[str, None] = '301576e22585'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index('ix_user_sessions_id', table_name='user_sessions')
    op.drop_constraint('user_sessions_session_token_key', 'user_sessions', type_='unique')
    op.drop_table('user_sessions')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=256), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_sessions_id', 'user_sessions', ['id'], unique=False)
    op.create_unique_constraint('user_sessions_session_token_key', 'user_sessions', ['session_token'])
