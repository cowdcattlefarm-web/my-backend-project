"""create animal events table

Revision ID: 20260514_1700
Revises: 20260514_1745
Create Date: 2026-05-14 17:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260514_1700"
down_revision: str | None = "20260514_1745"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "animal_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("animal_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.String(length=255), nullable=True),
        sa.Column("vet_name", sa.String(length=255), nullable=True),
        sa.Column("medicine_name", sa.String(length=255), nullable=True),
        sa.Column("dosage", sa.String(length=255), nullable=True),
        sa.Column("cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("attachment_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["animal_id"], ["animals.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_animal_events_animal_id"), "animal_events", ["animal_id"], unique=False)
    op.create_index(op.f("ix_animal_events_event_date"), "animal_events", ["event_date"], unique=False)
    op.create_index(op.f("ix_animal_events_event_type"), "animal_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_animal_events_id"), "animal_events", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_animal_events_id"), table_name="animal_events")
    op.drop_index(op.f("ix_animal_events_event_type"), table_name="animal_events")
    op.drop_index(op.f("ix_animal_events_event_date"), table_name="animal_events")
    op.drop_index(op.f("ix_animal_events_animal_id"), table_name="animal_events")
    op.drop_table("animal_events")
