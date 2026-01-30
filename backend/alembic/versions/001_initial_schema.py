"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'family_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('date_of_birth', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'scans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scan_type', sa.Enum('FULL', 'BREACH', 'DATA_BROKER', name='scantype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='scanstatus'), nullable=False),
        sa.Column('exposures_found', sa.Integer(), nullable=False, default=0),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'exposures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_member_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.Enum('DATA_BROKER', 'BREACH', 'PEOPLE_SEARCH', 'OTHER', name='exposuresource'), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('data_exposed', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DETECTED', 'REMOVAL_REQUESTED', 'REMOVAL_IN_PROGRESS', 'REMOVED', 'REMOVAL_FAILED', name='exposurestatus'), nullable=False),
        sa.Column('incogni_request_id', sa.String(length=255), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_member_id'], ['family_members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_exposures_family_member_id', 'exposures', ['family_member_id'])
    op.create_index('ix_exposures_status', 'exposures', ['status'])


def downgrade() -> None:
    op.drop_index('ix_exposures_status', table_name='exposures')
    op.drop_index('ix_exposures_family_member_id', table_name='exposures')
    op.drop_table('exposures')
    op.drop_table('scans')
    op.drop_table('family_members')

    op.execute("DROP TYPE IF EXISTS exposurestatus")
    op.execute("DROP TYPE IF EXISTS exposuresource")
    op.execute("DROP TYPE IF EXISTS scanstatus")
    op.execute("DROP TYPE IF EXISTS scantype")
