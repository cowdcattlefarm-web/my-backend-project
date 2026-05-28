"""create expense entries table

Revision ID: 20260514_1915
Revises: 20260514_1845
Create Date: 2026-05-14 19:15:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260514_1915"
down_revision: str | None = "20260514_1845"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "expense_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("expense_type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payment_mode", sa.String(length=50), nullable=False),
        sa.Column("vendor_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("animal_id", sa.Integer(), nullable=True),
        sa.Column("animal_event_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["animal_id"], ["animals.id"]),
        sa.ForeignKeyConstraint(["animal_event_id"], ["animal_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expense_entries_amount"), "expense_entries", ["amount"], unique=False)
    op.create_index(op.f("ix_expense_entries_animal_event_id"), "expense_entries", ["animal_event_id"], unique=False)
    op.create_index(op.f("ix_expense_entries_animal_id"), "expense_entries", ["animal_id"], unique=False)
    op.create_index(op.f("ix_expense_entries_expense_date"), "expense_entries", ["expense_date"], unique=False)
    op.create_index(op.f("ix_expense_entries_expense_type"), "expense_entries", ["expense_type"], unique=False)
    op.create_index(op.f("ix_expense_entries_id"), "expense_entries", ["id"], unique=False)
    op.create_index(op.f("ix_expense_entries_payment_mode"), "expense_entries", ["payment_mode"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_expense_entries_payment_mode"), table_name="expense_entries")
    op.drop_index(op.f("ix_expense_entries_id"), table_name="expense_entries")
    op.drop_index(op.f("ix_expense_entries_expense_type"), table_name="expense_entries")
    op.drop_index(op.f("ix_expense_entries_expense_date"), table_name="expense_entries")
    op.drop_index(op.f("ix_expense_entries_animal_id"), table_name="expense_entries")
    op.drop_index(op.f("ix_expense_entries_animal_event_id"), table_name="expense_entries")
    op.drop_index(op.f("ix_expense_entries_amount"), table_name="expense_entries")
    op.drop_table("expense_entries")
