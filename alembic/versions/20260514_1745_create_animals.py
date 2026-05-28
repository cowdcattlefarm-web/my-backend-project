"""create animals table

Revision ID: 20260514_1745
Revises:
Create Date: 2026-05-14 17:45:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260514_1745"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "animals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("animal_code", sa.String(length=50), nullable=False),
        sa.Column("tag_number", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("animal_type", sa.String(length=50), nullable=False),
        sa.Column("breed", sa.String(length=100), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("color", sa.String(length=100), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("purchase_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("current_status", sa.String(length=50), nullable=False),
        sa.Column("lactation_number", sa.Integer(), nullable=True),
        sa.Column("mother_id", sa.Integer(), nullable=True),
        sa.Column("father_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["father_id"], ["animals.id"]),
        sa.ForeignKeyConstraint(["mother_id"], ["animals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("animal_code"),
        sa.UniqueConstraint("tag_number"),
    )
    op.create_index(op.f("ix_animals_animal_code"), "animals", ["animal_code"], unique=True)
    op.create_index(op.f("ix_animals_animal_type"), "animals", ["animal_type"], unique=False)
    op.create_index(op.f("ix_animals_breed"), "animals", ["breed"], unique=False)
    op.create_index(op.f("ix_animals_current_status"), "animals", ["current_status"], unique=False)
    op.create_index(op.f("ix_animals_father_id"), "animals", ["father_id"], unique=False)
    op.create_index(op.f("ix_animals_id"), "animals", ["id"], unique=False)
    op.create_index(op.f("ix_animals_is_active"), "animals", ["is_active"], unique=False)
    op.create_index(op.f("ix_animals_mother_id"), "animals", ["mother_id"], unique=False)
    op.create_index(op.f("ix_animals_tag_number"), "animals", ["tag_number"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_animals_tag_number"), table_name="animals")
    op.drop_index(op.f("ix_animals_mother_id"), table_name="animals")
    op.drop_index(op.f("ix_animals_is_active"), table_name="animals")
    op.drop_index(op.f("ix_animals_id"), table_name="animals")
    op.drop_index(op.f("ix_animals_father_id"), table_name="animals")
    op.drop_index(op.f("ix_animals_current_status"), table_name="animals")
    op.drop_index(op.f("ix_animals_breed"), table_name="animals")
    op.drop_index(op.f("ix_animals_animal_type"), table_name="animals")
    op.drop_index(op.f("ix_animals_animal_code"), table_name="animals")
    op.drop_table("animals")
