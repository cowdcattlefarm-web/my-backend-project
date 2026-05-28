from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.milk_entry import MilkEntry
from app.schemas.animal import AnimalStatus
from app.schemas.milk_entry import MilkEntryCreate, MilkEntryUpdate


class MilkEntryService:
    @staticmethod
    def _to_decimal(value: Decimal | int | float) -> Decimal:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_animal(db: Session, animal_id: int) -> Animal | None:
        return db.get(Animal, animal_id)

    @staticmethod
    def is_animal_milking(animal: Animal) -> bool:
        return animal.current_status == AnimalStatus.milking.value

    @staticmethod
    def get_milk_entry(db: Session, milk_entry_id: int) -> MilkEntry | None:
        return db.get(MilkEntry, milk_entry_id)

    @staticmethod
    def duplicate_entry_exists(
        db: Session,
        *,
        animal_id: int,
        entry_date: date,
        shift: str,
        exclude_id: int | None = None,
    ) -> bool:
        query = select(MilkEntry.id).where(
            MilkEntry.animal_id == animal_id,
            MilkEntry.entry_date == entry_date,
            MilkEntry.shift == shift,
        )
        if exclude_id is not None:
            query = query.where(MilkEntry.id != exclude_id)
        return db.scalar(query) is not None

    @staticmethod
    def create_milk_entry(db: Session, payload: MilkEntryCreate) -> MilkEntry:
        milk_entry = MilkEntry(**payload.model_dump(mode="python"))
        db.add(milk_entry)
        db.commit()
        db.refresh(milk_entry)
        return milk_entry

    @staticmethod
    def update_milk_entry(db: Session, milk_entry: MilkEntry, payload: MilkEntryUpdate) -> MilkEntry:
        updates = payload.model_dump(mode="python", exclude_unset=True)
        for field, value in updates.items():
            setattr(milk_entry, field, value)

        db.commit()
        db.refresh(milk_entry)
        return milk_entry

    @staticmethod
    def delete_milk_entry(db: Session, milk_entry: MilkEntry) -> None:
        db.delete(milk_entry)
        db.commit()

    @staticmethod
    def list_milk_entries(
        db: Session,
        *,
        animal_id: int | None,
        entry_date: date | None,
        shift: str | None,
    ) -> list[MilkEntry]:
        query = select(MilkEntry)

        if animal_id is not None:
            query = query.where(MilkEntry.animal_id == animal_id)
        if entry_date is not None:
            query = query.where(MilkEntry.entry_date == entry_date)
        if shift is not None:
            query = query.where(MilkEntry.shift == shift)

        return db.scalars(
            query.order_by(MilkEntry.entry_date.desc(), MilkEntry.id.desc())
        ).all()

    @staticmethod
    def get_daily_summary(db: Session, entry_date: date) -> Decimal:
        total = db.scalar(
            select(func.coalesce(func.sum(MilkEntry.quantity_liters), 0)).where(MilkEntry.entry_date == entry_date)
        )
        return MilkEntryService._to_decimal(total)

    @staticmethod
    def get_monthly_summary(db: Session, year: int, month: int) -> list[tuple[date, Decimal]]:
        rows = db.execute(
            select(
                MilkEntry.entry_date,
                func.coalesce(func.sum(MilkEntry.quantity_liters), 0).label("total_quantity_liters"),
            )
            .where(
                func.extract("year", MilkEntry.entry_date) == year,
                func.extract("month", MilkEntry.entry_date) == month,
            )
            .group_by(MilkEntry.entry_date)
            .order_by(MilkEntry.entry_date.asc())
        ).all()

        return [
            (
                row.entry_date,
                MilkEntryService._to_decimal(row.total_quantity_liters),
            )
            for row in rows
        ]

    @staticmethod
    def get_animal_summary(db: Session, animal_id: int) -> tuple[Decimal, Decimal, int]:
        row = db.execute(
            select(
                func.coalesce(func.sum(MilkEntry.quantity_liters), 0).label("total_quantity_liters"),
                func.coalesce(func.avg(MilkEntry.quantity_liters), 0).label("average_quantity_liters"),
                func.count(MilkEntry.id).label("entry_count"),
            ).where(MilkEntry.animal_id == animal_id)
        ).one()

        total = MilkEntryService._to_decimal(row.total_quantity_liters)
        average = MilkEntryService._to_decimal(row.average_quantity_liters)
        return total, average, row.entry_count
