"""add abacatepay_client_id in usermodel

Revision ID: d7295eeef4b8
Revises: c80b7cf03f6b
Create Date: 2025-06-07 11:55:21.181802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7295eeef4b8'
down_revision: Union[str, None] = 'c80b7cf03f6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('abacatepay_client_id', sa.Integer()))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
