"""Add exam_task_number column and unique constraint to curriculum_nodes

Revision ID: a2f8c3d9e1b0
Revises: 7e9424fcd3ae
Create Date: 2026-02-23 12:00:00.000000

Changes:
  1. ADD COLUMN curriculum_nodes.exam_task_number VARCHAR(16) (if not already present)
  2. ADD UNIQUE INDEX uq_curriculum_nodes_curriculum_canonical
     ON curriculum_nodes(curriculum_id, canonical_uid)
     — prevents duplicate topic entries within the same curriculum
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a2f8c3d9e1b0"
down_revision: Union[str, Sequence[str], None] = "7e9424fcd3ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add exam_task_number column (was missing from initial schema)
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='curriculum_nodes' AND column_name='exam_task_number'"
        )
    )
    if result.fetchone() is None:
        op.add_column(
            "curriculum_nodes",
            sa.Column("exam_task_number", sa.String(length=16), nullable=True),
        )

    # 2. Remove any existing duplicate (curriculum_id, canonical_uid) rows,
    #    keeping only the one with the lowest id (order_index tiebreak).
    conn.execute(
        sa.text(
            """
            DELETE FROM curriculum_nodes
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM curriculum_nodes
                GROUP BY curriculum_id, canonical_uid
            )
            """
        )
    )

    # 3. Create unique index
    op.create_index(
        "uq_curriculum_nodes_curriculum_canonical",
        "curriculum_nodes",
        ["curriculum_id", "canonical_uid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_curriculum_nodes_curriculum_canonical",
        table_name="curriculum_nodes",
    )
    # Note: we intentionally keep the exam_task_number column on downgrade
    # to avoid data loss from already-populated rows.
