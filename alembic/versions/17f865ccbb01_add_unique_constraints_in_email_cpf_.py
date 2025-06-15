"""add unique constraints in email, cpf_cnpj and cellphone in user model

Revision ID: 17f865ccbb01
Revises: d06f7d662627
Create Date: 2025-06-14 22:51:02.485766

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '17f865ccbb01'
down_revision: Union[str, None] = 'd06f7d662627'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_users_cpf_cnpj', 'users', ['cpf_cnpj'])
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_unique_constraint('uq_users_cellphone', 'users', ['cellphone'])


def downgrade() -> None:
    """Downgrade schema."""
    pass
