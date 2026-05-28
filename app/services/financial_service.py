from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense_entry import ExpenseEntry
from app.models.income_entry import IncomeEntry


class FinancialService:
    @staticmethod
    def _to_decimal(value: Decimal | int | float | None) -> Decimal:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value or 0))
        return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_summary(
        db: Session,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> dict[str, Decimal | int]:
        income_filters = []
        expense_filters = []

        if date_from is not None:
            income_filters.append(IncomeEntry.income_date >= date_from)
            expense_filters.append(ExpenseEntry.expense_date >= date_from)
        if date_to is not None:
            income_filters.append(IncomeEntry.income_date <= date_to)
            expense_filters.append(ExpenseEntry.expense_date <= date_to)

        total_income = FinancialService._to_decimal(
            db.scalar(select(func.coalesce(func.sum(IncomeEntry.amount), 0)).where(*income_filters))
        )
        total_expense = FinancialService._to_decimal(
            db.scalar(select(func.coalesce(func.sum(ExpenseEntry.amount), 0)).where(*expense_filters))
        )
        income_count = db.scalar(select(func.count(IncomeEntry.id)).where(*income_filters)) or 0
        expense_count = db.scalar(select(func.count(ExpenseEntry.id)).where(*expense_filters)) or 0

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "profit_or_loss": total_income - total_expense,
            "income_count": income_count,
            "expense_count": expense_count,
        }

    @staticmethod
    def get_category_summary(
        db: Session,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> dict[str, list[dict[str, Decimal | int | str]]]:
        income_filters = []
        expense_filters = []

        if date_from is not None:
            income_filters.append(IncomeEntry.income_date >= date_from)
            expense_filters.append(ExpenseEntry.expense_date >= date_from)
        if date_to is not None:
            income_filters.append(IncomeEntry.income_date <= date_to)
            expense_filters.append(ExpenseEntry.expense_date <= date_to)

        income_rows = db.execute(
            select(
                IncomeEntry.income_type,
                func.coalesce(func.sum(IncomeEntry.amount), 0),
                func.count(IncomeEntry.id),
            )
            .where(*income_filters)
            .group_by(IncomeEntry.income_type)
            .order_by(IncomeEntry.income_type)
        ).all()
        expense_rows = db.execute(
            select(
                ExpenseEntry.expense_type,
                func.coalesce(func.sum(ExpenseEntry.amount), 0),
                func.count(ExpenseEntry.id),
            )
            .where(*expense_filters)
            .group_by(ExpenseEntry.expense_type)
            .order_by(ExpenseEntry.expense_type)
        ).all()

        return {
            "income": [
                {
                    "income_type": income_type,
                    "total_amount": FinancialService._to_decimal(total_amount),
                    "count": count,
                }
                for income_type, total_amount, count in income_rows
            ],
            "expenses": [
                {
                    "expense_type": expense_type,
                    "total_amount": FinancialService._to_decimal(total_amount),
                    "count": count,
                }
                for expense_type, total_amount, count in expense_rows
            ],
        }
