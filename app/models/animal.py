from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    animal_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    tag_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    animal_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    breed: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    lactation_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mother_id: Mapped[int | None] = mapped_column(ForeignKey("animals.id"), nullable=True, index=True)
    father_id: Mapped[int | None] = mapped_column(ForeignKey("animals.id"), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"), default=True, index=True)
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

    mother: Mapped["Animal | None"] = relationship(
        "Animal",
        foreign_keys=[mother_id],
        remote_side="Animal.id",
    )
    father: Mapped["Animal | None"] = relationship(
        "Animal",
        foreign_keys=[father_id],
        remote_side="Animal.id",
    )
    events: Mapped[list["AnimalEvent"]] = relationship(back_populates="animal")
    milk_entries: Mapped[list["MilkEntry"]] = relationship(back_populates="animal")
    income_entries: Mapped[list["IncomeEntry"]] = relationship(back_populates="animal")
    expense_entries: Mapped[list["ExpenseEntry"]] = relationship(back_populates="animal")
