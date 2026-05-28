from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.animal_event import AnimalEvent
from app.models.expense_entry import ExpenseEntry
from app.models.income_entry import IncomeEntry
from app.models.milk_entry import MilkEntry
from app.schemas.animal import AnimalStatus
from app.schemas.animal_event import AnimalEventType


class DashboardService:
    @staticmethod
    def _to_decimal(value: Decimal | int | float | None) -> Decimal:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value or 0))
        return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _month_range(today: date) -> tuple[date, date]:
        month_start = today.replace(day=1)
        if today.month == 12:
            next_month_start = date(today.year + 1, 1, 1)
        else:
            next_month_start = date(today.year, today.month + 1, 1)
        return month_start, next_month_start - timedelta(days=1)

    @staticmethod
    def _animal_count(db: Session, *filters) -> int:
        return db.scalar(select(func.count(Animal.id)).where(Animal.is_active.is_(True), *filters)) or 0

    @staticmethod
    def _milk_total(db: Session, *, date_from: date, date_to: date) -> Decimal:
        total = db.scalar(
            select(func.coalesce(func.sum(MilkEntry.quantity_liters), 0)).where(
                MilkEntry.entry_date >= date_from,
                MilkEntry.entry_date <= date_to,
            )
        )
        return DashboardService._to_decimal(total)

    @staticmethod
    def _income_total(db: Session, *, date_from: date, date_to: date) -> Decimal:
        total = db.scalar(
            select(func.coalesce(func.sum(IncomeEntry.amount), 0)).where(
                IncomeEntry.income_date >= date_from,
                IncomeEntry.income_date <= date_to,
            )
        )
        return DashboardService._to_decimal(total)

    @staticmethod
    def _expense_total(db: Session, *, date_from: date, date_to: date) -> Decimal:
        total = db.scalar(
            select(func.coalesce(func.sum(ExpenseEntry.amount), 0)).where(
                ExpenseEntry.expense_date >= date_from,
                ExpenseEntry.expense_date <= date_to,
            )
        )
        return DashboardService._to_decimal(total)

    @staticmethod
    def get_summary(db: Session, today: date) -> dict[str, int | Decimal]:
        month_start, month_end = DashboardService._month_range(today)
        monthly_income = DashboardService._income_total(db, date_from=month_start, date_to=month_end)
        monthly_expense = DashboardService._expense_total(db, date_from=month_start, date_to=month_end)

        return {
            "total_animals": DashboardService._animal_count(db),
            "milking_animals": DashboardService._animal_count(
                db, Animal.current_status == AnimalStatus.milking.value
            ),
            "pregnant_animals": DashboardService._animal_count(
                db, Animal.current_status == AnimalStatus.pregnant.value
            ),
            "dry_animals": DashboardService._animal_count(db, Animal.current_status == AnimalStatus.dry.value),
            "calves": DashboardService._animal_count(db, Animal.current_status == AnimalStatus.calf.value),
            "sick_animals": DashboardService._animal_count(db, Animal.current_status == AnimalStatus.sick.value),
            "today_total_milk": DashboardService._milk_total(db, date_from=today, date_to=today),
            "monthly_total_milk": DashboardService._milk_total(db, date_from=month_start, date_to=month_end),
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "monthly_profit_or_loss": monthly_income - monthly_expense,
        }

    @staticmethod
    def get_milk_trend(db: Session, *, date_from: date, date_to: date) -> list[dict[str, date | Decimal]]:
        rows = db.execute(
            select(
                MilkEntry.entry_date,
                func.coalesce(func.sum(MilkEntry.quantity_liters), 0).label("total_quantity_liters"),
            )
            .where(MilkEntry.entry_date >= date_from, MilkEntry.entry_date <= date_to)
            .group_by(MilkEntry.entry_date)
            .order_by(MilkEntry.entry_date.asc())
        ).all()

        return [
            {
                "date": row.entry_date,
                "total_quantity_liters": DashboardService._to_decimal(row.total_quantity_liters),
            }
            for row in rows
        ]

    @staticmethod
    def get_financial_summary(db: Session, *, date_from: date, date_to: date) -> dict[str, Decimal]:
        total_income = DashboardService._income_total(db, date_from=date_from, date_to=date_to)
        total_expense = DashboardService._expense_total(db, date_from=date_from, date_to=date_to)
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "profit_or_loss": total_income - total_expense,
        }

    @staticmethod
    def get_upcoming_events(db: Session, today: date) -> list[AnimalEvent]:
        due_until = today + timedelta(days=30)
        return db.scalars(
            select(AnimalEvent)
            .where(AnimalEvent.next_due_date >= today, AnimalEvent.next_due_date <= due_until)
            .order_by(AnimalEvent.next_due_date.asc(), AnimalEvent.id.asc())
        ).all()

    @staticmethod
    def get_alerts(db: Session, today: date) -> dict[str, list[Animal] | list[AnimalEvent]]:
        due_until = today + timedelta(days=30)
        sick_animals = db.scalars(
            select(Animal)
            .where(
                Animal.is_active.is_(True),
                Animal.current_status == AnimalStatus.sick.value,
            )
            .order_by(Animal.id.asc())
        ).all()
        upcoming_vaccinations = db.scalars(
            select(AnimalEvent)
            .where(
                AnimalEvent.event_type == AnimalEventType.vaccination.value,
                AnimalEvent.next_due_date >= today,
                AnimalEvent.next_due_date <= due_until,
            )
            .order_by(AnimalEvent.next_due_date.asc(), AnimalEvent.id.asc())
        ).all()
        upcoming_deworming = db.scalars(
            select(AnimalEvent)
            .where(
                AnimalEvent.event_type == AnimalEventType.deworming.value,
                AnimalEvent.next_due_date >= today,
                AnimalEvent.next_due_date <= due_until,
            )
            .order_by(AnimalEvent.next_due_date.asc(), AnimalEvent.id.asc())
        ).all()
        milking_without_milk_entry_today = db.scalars(
            select(Animal)
            .where(
                Animal.is_active.is_(True),
                Animal.current_status == AnimalStatus.milking.value,
                ~select(MilkEntry.id)
                .where(MilkEntry.animal_id == Animal.id, MilkEntry.entry_date == today)
                .exists(),
            )
            .order_by(Animal.id.asc())
        ).all()

        return {
            "sick_animals": sick_animals,
            "upcoming_vaccinations": upcoming_vaccinations,
            "upcoming_deworming": upcoming_deworming,
            "milking_animals_without_milk_entry_today": milking_without_milk_entry_today,
        }
