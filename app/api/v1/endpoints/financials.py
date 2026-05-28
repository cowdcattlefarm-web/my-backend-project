from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.services.financial_service import FinancialService
from app.utils.responses import error_response, success_response

router = APIRouter(prefix="/financials")


def _serialize_money(value: Decimal) -> str:
    return str(value)


def _serialize_summary(summary: dict[str, Decimal | int]) -> dict[str, str | int]:
    return {
        "total_income": _serialize_money(summary["total_income"]),
        "total_expense": _serialize_money(summary["total_expense"]),
        "profit_or_loss": _serialize_money(summary["profit_or_loss"]),
        "income_count": summary["income_count"],
        "expense_count": summary["expense_count"],
    }


def _serialize_category_summary(category_summary: dict) -> dict:
    return {
        "income": [
            {
                "income_type": item["income_type"],
                "total_amount": _serialize_money(item["total_amount"]),
                "count": item["count"],
            }
            for item in category_summary["income"]
        ],
        "expenses": [
            {
                "expense_type": item["expense_type"],
                "total_amount": _serialize_money(item["total_amount"]),
                "count": item["count"],
            }
            for item in category_summary["expenses"]
        ],
    }


def _bad_request_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response(message=message),
    )


def _validate_date_range(date_from: date | None, date_to: date | None) -> JSONResponse | None:
    if date_from is not None and date_to is not None and date_from > date_to:
        return _bad_request_response("date_from must be before or equal to date_to.")
    return None


def _parse_month(month: str) -> tuple[date, date] | None:
    try:
        year_text, month_text = month.split("-", maxsplit=1)
        year = int(year_text)
        month_number = int(month_text)
        month_start = date(year, month_number, 1)
    except ValueError:
        return None

    if month_number == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month_number + 1, 1)

    return month_start, next_month_start - timedelta(days=1)


@router.get("/summary", response_model=ApiResponse)
def get_financial_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    validation_error = _validate_date_range(date_from, date_to)
    if validation_error:
        return validation_error

    summary = FinancialService.get_summary(db, date_from=date_from, date_to=date_to)
    return success_response(
        message="Financial summary fetched successfully.",
        data=_serialize_summary(summary),
    )


@router.get("/profit-loss", response_model=ApiResponse)
def get_profit_loss(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", examples=["2026-05"]),
    db: Session = Depends(get_db),
):
    month_range = _parse_month(month)
    if month_range is None:
        return _bad_request_response("month must be in YYYY-MM format.")

    month_start, next_month_start = month_range
    summary = FinancialService.get_summary(
        db,
        date_from=month_start,
        date_to=next_month_start,
    )
    return success_response(
        message="Profit-loss summary fetched successfully.",
        data={
            "month": month,
            "total_income": _serialize_money(summary["total_income"]),
            "total_expense": _serialize_money(summary["total_expense"]),
            "profit_or_loss": _serialize_money(summary["profit_or_loss"]),
        },
    )


@router.get("/category-summary", response_model=ApiResponse)
def get_category_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    validation_error = _validate_date_range(date_from, date_to)
    if validation_error:
        return validation_error

    category_summary = FinancialService.get_category_summary(db, date_from=date_from, date_to=date_to)
    return success_response(
        message="Financial category summary fetched successfully.",
        data=_serialize_category_summary(category_summary),
    )
