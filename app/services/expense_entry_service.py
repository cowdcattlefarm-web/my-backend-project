from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.animal_event import AnimalEvent
from app.models.expense_entry import ExpenseEntry
from app.schemas.expense_entry import ExpenseEntryCreate, ExpenseEntryUpdate


class ExpenseEntryService:
    @staticmethod
    def _to_decimal(value: Decimal | int | float) -> Decimal:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_expense_entry(db: Session, expense_id: int) -> ExpenseEntry | None:
        return db.get(ExpenseEntry, expense_id)

    @staticmethod
    def get_animal(db: Session, animal_id: int) -> Animal | None:
        return db.get(Animal, animal_id)

    @staticmethod
    def get_animal_event(db: Session, animal_event_id: int) -> AnimalEvent | None:
        return db.get(AnimalEvent, animal_event_id)

    @staticmethod
    def create_expense_entry(db: Session, payload: ExpenseEntryCreate) -> ExpenseEntry:
        expense_entry = ExpenseEntry(**payload.model_dump(mode="python"))
        db.add(expense_entry)
        db.commit()
        db.refresh(expense_entry)
        return expense_entry

    @staticmethod
    def update_expense_entry(db: Session, expense_entry: ExpenseEntry, payload: ExpenseEntryUpdate) -> ExpenseEntry:
        updates = payload.model_dump(mode="python", exclude_unset=True)
        for field, value in updates.items():
            setattr(expense_entry, field, value)

        db.commit()
        db.refresh(expense_entry)
        return expense_entry

    @staticmethod
    def delete_expense_entry(db: Session, expense_entry: ExpenseEntry) -> None:
        db.delete(expense_entry)
        db.commit()

    @staticmethod
    def list_expense_entries(
        db: Session,
        *,
        page: int,
        limit: int,
        expense_type: str | None,
        payment_mode: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[list[ExpenseEntry], int, Decimal]:
        filters = []

        if expense_type is not None:
            filters.append(ExpenseEntry.expense_type == expense_type)
        if payment_mode is not None:
            filters.append(ExpenseEntry.payment_mode == payment_mode)
        if date_from is not None:
            filters.append(ExpenseEntry.expense_date >= date_from)
        if date_to is not None:
            filters.append(ExpenseEntry.expense_date <= date_to)

        base_query = select(ExpenseEntry).where(*filters)
        total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        total_expense_amount = db.scalar(
            select(func.coalesce(func.sum(ExpenseEntry.amount), 0)).where(*filters)
        )

        expense_entries = db.scalars(
            base_query
            .order_by(ExpenseEntry.expense_date.desc(), ExpenseEntry.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()

        return expense_entries, total, ExpenseEntryService._to_decimal(total_expense_amount)
