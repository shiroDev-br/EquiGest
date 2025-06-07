""".

Revision ID: a117b1368f9c
Revises: ab5ea0aaa1af
Create Date: 2025-06-07 09:39:11.129754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a117b1368f9c'
down_revision: Union[str, None] = 'ab5ea0aaa1af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('payment_status', sa.String(length=20), nullable=False, server_default='TRIAL'))
    op.add_column('users', sa.Column('next_payment_date', sa.DateTime(timezone=True), nullable=True))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
