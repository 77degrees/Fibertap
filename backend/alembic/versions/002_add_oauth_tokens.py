"""Add OAuth tokens table

Revision ID: 002
Revises: 001
Create Date: 2024-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'oauth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_type', sa.String(length=50), nullable=True, default='Bearer'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_oauth_tokens_provider', 'oauth_tokens', ['provider'])


def downgrade() -> None:
    op.drop_index('ix_oauth_tokens_provider', table_name='oauth_tokens')
    op.drop_table('oauth_tokens')
