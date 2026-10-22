"""add phone column to customers

Revision ID: d28537ee5cf4
Revises: 4e1f04656543
Create Date: 2026-10-22 16:55:05.417422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd28537ee5cf4'
down_revision: Union[str, Sequence[str], None] = '4e1f04656543'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
