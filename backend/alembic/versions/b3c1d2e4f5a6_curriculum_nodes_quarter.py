"""Add quarter column to curriculum_nodes (school quarter curricula)

Revision ID: b3c1d2e4f5a6
Revises: a2f8c3d9e1b0
Create Date: 2026-06-13 12:00:00.000000

Changes:
  1. ADD COLUMN curriculum_nodes.quarter SMALLINT NULL (if not already present)
     — marks which school quarter (1..4) a curriculum node belongs to.
       NULL = quarter-agnostic node (e.g. exam curricula keep it NULL).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3c1d2e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a2f8c3d9e1b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='curriculum_nodes' AND column_name='quarter'"
        )
    )
    if result.fetchone() is None:
        op.add_column(
            "curriculum_nodes",
            sa.Column("quarter", sa.SmallInteger(), nullable=True),
        )


def downgrade() -> None:
    # Keep the column on downgrade to avoid data loss from populated rows.
    pass
