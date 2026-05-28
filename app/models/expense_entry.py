from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExpenseEntry(Base):
    __tablename__ = "expense_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expense_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, index=True)
    payment_mode: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    animal_id: Mapped[int | None] = mapped_column(ForeignKey("animals.id"), nullable=True, index=True)
    animal_event_id: Mapped[int | None] = mapped_column(ForeignKey("animal_events.id"), nullable=True, index=True)
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

    animal: Mapped["Animal | None"] = relationship(back_populates="expense_entries")
    animal_event: Mapped["AnimalEvent | None"] = relationship(back_populates="expense_entries")
