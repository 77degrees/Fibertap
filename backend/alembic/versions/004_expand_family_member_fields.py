"""Expand family member fields for better data broker matching

Revision ID: 004
Revises: 003
Create Date: 2024-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new name fields
    op.add_column('family_members', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('family_members', sa.Column('middle_initial', sa.String(5), nullable=True))
    op.add_column('family_members', sa.Column('last_name', sa.String(100), nullable=True))

    # Add JSON array fields for multiple entries
    op.add_column('family_members', sa.Column('emails', sa.JSON(), nullable=True))
    op.add_column('family_members', sa.Column('phone_numbers', sa.JSON(), nullable=True))
    op.add_column('family_members', sa.Column('addresses', sa.JSON(), nullable=True))

    # Migrate existing data: split name into first/last, move single values to arrays
    op.execute("""
        UPDATE family_members SET
            first_name = SPLIT_PART(name, ' ', 1),
            last_name = CASE
                WHEN POSITION(' ' IN name) > 0
                THEN SUBSTRING(name FROM POSITION(' ' IN name) + 1)
                ELSE name
            END,
            emails = CASE WHEN email IS NOT NULL THEN json_build_array(email) ELSE '[]' END,
            phone_numbers = CASE WHEN phone IS NOT NULL THEN json_build_array(phone) ELSE '[]' END,
            addresses = CASE WHEN address IS NOT NULL THEN json_build_array(address) ELSE '[]' END
    """)

    # Make first_name and last_name required after migration
    op.alter_column('family_members', 'first_name', nullable=False)
    op.alter_column('family_members', 'last_name', nullable=False)


def downgrade() -> None:
    op.drop_column('family_members', 'addresses')
    op.drop_column('family_members', 'phone_numbers')
    op.drop_column('family_members', 'emails')
    op.drop_column('family_members', 'last_name')
    op.drop_column('family_members', 'middle_initial')
    op.drop_column('family_members', 'first_name')
