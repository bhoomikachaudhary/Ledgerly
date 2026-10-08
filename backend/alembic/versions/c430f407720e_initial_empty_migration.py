"""initial empty migration

Revision ID: c430f407720e
Revises:
Create Date: 2026-09-24 00:00:00

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c430f407720e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
