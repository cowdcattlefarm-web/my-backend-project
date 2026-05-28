from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.income_entry import IncomeEntry
from app.models.milk_entry import MilkEntry
from app.schemas.income_entry import IncomeEntryCreate, IncomeEntryUpdate


class IncomeEntryService:
    @staticmethod
    def _to_decimal(value: Decimal | int | float) -> Decimal:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_income_entry(db: Session, income_id: int) -> IncomeEntry | None:
        return db.get(IncomeEntry, income_id)

    @staticmethod
    def get_animal(db: Session, animal_id: int) -> Animal | None:
        return db.get(Animal, animal_id)

    @staticmethod
    def get_milk_entry(db: Session, milk_entry_id: int) -> MilkEntry | None:
        return db.get(MilkEntry, milk_entry_id)

    @staticmethod
    def create_income_entry(db: Session, payload: IncomeEntryCreate) -> IncomeEntry:
        income_entry = IncomeEntry(**payload.model_dump(mode="python"))
        db.add(income_entry)
        db.commit()
        db.refresh(income_entry)
        return income_entry

    @staticmethod
    def update_income_entry(db: Session, income_entry: IncomeEntry, payload: IncomeEntryUpdate) -> IncomeEntry:
        updates = payload.model_dump(mode="python", exclude_unset=True)
        for field, value in updates.items():
            setattr(income_entry, field, value)

        db.commit()
        db.refresh(income_entry)
        return income_entry

    @staticmethod
    def delete_income_entry(db: Session, income_entry: IncomeEntry) -> None:
        db.delete(income_entry)
        db.commit()

    @staticmethod
    def list_income_entries(
        db: Session,
        *,
        page: int,
        limit: int,
        income_type: str | None,
        payment_mode: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[list[IncomeEntry], int, Decimal]:
        filters = []

        if income_type is not None:
            filters.append(IncomeEntry.income_type == income_type)
        if payment_mode is not None:
            filters.append(IncomeEntry.payment_mode == payment_mode)
        if date_from is not None:
            filters.append(IncomeEntry.income_date >= date_from)
        if date_to is not None:
            filters.append(IncomeEntry.income_date <= date_to)

        base_query = select(IncomeEntry).where(*filters)
        total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        total_income_amount = db.scalar(
            select(func.coalesce(func.sum(IncomeEntry.amount), 0)).where(*filters)
        )

        income_entries = db.scalars(
            base_query
            .order_by(IncomeEntry.income_date.desc(), IncomeEntry.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()

        return income_entries, total, IncomeEntryService._to_decimal(total_income_amount)
