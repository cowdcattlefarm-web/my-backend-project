"""create milk entries table

Revision ID: 20260514_1815
Revises: 20260514_1700
Create Date: 2026-05-14 18:15:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260514_1815"
down_revision: str | None = "20260514_1700"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "milk_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("animal_id", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("shift", sa.String(length=20), nullable=False),
        sa.Column("quantity_liters", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("fat_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("snf_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("milk_quality_notes", sa.Text(), nullable=True),
        sa.Column("recorded_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["animal_id"], ["animals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("animal_id", "entry_date", "shift", name="uq_milk_entries_animal_date_shift"),
    )
    op.create_index(op.f("ix_milk_entries_animal_id"), "milk_entries", ["animal_id"], unique=False)
    op.create_index(op.f("ix_milk_entries_entry_date"), "milk_entries", ["entry_date"], unique=False)
    op.create_index(op.f("ix_milk_entries_id"), "milk_entries", ["id"], unique=False)
    op.create_index(op.f("ix_milk_entries_shift"), "milk_entries", ["shift"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_milk_entries_shift"), table_name="milk_entries")
    op.drop_index(op.f("ix_milk_entries_id"), table_name="milk_entries")
    op.drop_index(op.f("ix_milk_entries_entry_date"), table_name="milk_entries")
    op.drop_index(op.f("ix_milk_entries_animal_id"), table_name="milk_entries")
    op.drop_table("milk_entries")
