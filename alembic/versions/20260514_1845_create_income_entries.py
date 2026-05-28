"""create income entries table

Revision ID: 20260514_1845
Revises: 20260514_1815
Create Date: 2026-05-14 18:45:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260514_1845"
down_revision: str | None = "20260514_1815"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "income_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("income_date", sa.Date(), nullable=False),
        sa.Column("income_type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payment_mode", sa.String(length=50), nullable=False),
        sa.Column("reference_number", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("animal_id", sa.Integer(), nullable=True),
        sa.Column("milk_entry_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["animal_id"], ["animals.id"]),
        sa.ForeignKeyConstraint(["milk_entry_id"], ["milk_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_income_entries_amount"), "income_entries", ["amount"], unique=False)
    op.create_index(op.f("ix_income_entries_animal_id"), "income_entries", ["animal_id"], unique=False)
    op.create_index(op.f("ix_income_entries_id"), "income_entries", ["id"], unique=False)
    op.create_index(op.f("ix_income_entries_income_date"), "income_entries", ["income_date"], unique=False)
    op.create_index(op.f("ix_income_entries_income_type"), "income_entries", ["income_type"], unique=False)
    op.create_index(op.f("ix_income_entries_milk_entry_id"), "income_entries", ["milk_entry_id"], unique=False)
    op.create_index(op.f("ix_income_entries_payment_mode"), "income_entries", ["payment_mode"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_income_entries_payment_mode"), table_name="income_entries")
    op.drop_index(op.f("ix_income_entries_milk_entry_id"), table_name="income_entries")
    op.drop_index(op.f("ix_income_entries_income_type"), table_name="income_entries")
    op.drop_index(op.f("ix_income_entries_income_date"), table_name="income_entries")
    op.drop_index(op.f("ix_income_entries_id"), table_name="income_entries")
    op.drop_index(op.f("ix_income_entries_animal_id"), table_name="income_entries")
    op.drop_index(op.f("ix_income_entries_amount"), table_name="income_entries")
    op.drop_table("income_entries")
