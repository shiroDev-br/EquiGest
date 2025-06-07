"""change the type of abacatepay_client_id field in usermodel

Revision ID: d06f7d662627
Revises: d7295eeef4b8
Create Date: 2025-06-07 13:16:57.402118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd06f7d662627'
down_revision: Union[str, None] = 'd7295eeef4b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'users', 
        'abacatepay_client_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=255),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
