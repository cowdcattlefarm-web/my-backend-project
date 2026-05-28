from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MilkEntry(Base):
    __tablename__ = "milk_entries"
    __table_args__ = (
        UniqueConstraint("animal_id", "entry_date", "shift", name="uq_milk_entries_animal_date_shift"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id"), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    shift: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    quantity_liters: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    snf_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    milk_quality_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    animal: Mapped["Animal"] = relationship(back_populates="milk_entries")
    income_entries: Mapped[list["IncomeEntry"]] = relationship(back_populates="milk_entry")
