from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.animal import Animal
from app.models.animal_event import AnimalEvent
from app.schemas.animal import AnimalRead
from app.schemas.animal_event import AnimalEventRead
from app.schemas.common import ApiResponse
from app.services.dashboard_service import DashboardService
from app.utils.responses import error_response, success_response

router = APIRouter(prefix="/dashboard")


def _serialize_decimal(value: Decimal) -> str:
    return str(value)


def _serialize_animal(animal: Animal) -> dict:
    return AnimalRead.model_validate(animal).model_dump(mode="json")


def _serialize_event(event: AnimalEvent) -> dict:
    return AnimalEventRead.model_validate(event).model_dump(mode="json")


def _bad_request_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response(message=message),
    )


def _validate_date_range(date_from: date, date_to: date) -> JSONResponse | None:
    if date_from > date_to:
        return _bad_request_response("date_from must be before or equal to date_to.")
    return None


@router.get("/summary", response_model=ApiResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    summary = DashboardService.get_summary(db, date.today())
    return success_response(
        message="Dashboard summary fetched successfully.",
        data={
            "total_animals": summary["total_animals"],
            "milking_animals": summary["milking_animals"],
            "pregnant_animals": summary["pregnant_animals"],
            "dry_animals": summary["dry_animals"],
            "calves": summary["calves"],
            "sick_animals": summary["sick_animals"],
            "today_total_milk": _serialize_decimal(summary["today_total_milk"]),
            "monthly_total_milk": _serialize_decimal(summary["monthly_total_milk"]),
            "monthly_income": _serialize_decimal(summary["monthly_income"]),
            "monthly_expense": _serialize_decimal(summary["monthly_expense"]),
            "monthly_profit_or_loss": _serialize_decimal(summary["monthly_profit_or_loss"]),
        },
    )


@router.get("/milk-trend", response_model=ApiResponse)
def get_milk_trend(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: Session = Depends(get_db),
):
    validation_error = _validate_date_range(date_from, date_to)
    if validation_error:
        return validation_error

    items = DashboardService.get_milk_trend(db, date_from=date_from, date_to=date_to)
    return success_response(
        message="Dashboard milk trend fetched successfully.",
        data=[
            {
                "date": item["date"].isoformat(),
                "total_quantity_liters": _serialize_decimal(item["total_quantity_liters"]),
            }
            for item in items
        ],
    )


@router.get("/financial-summary", response_model=ApiResponse)
def get_dashboard_financial_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: Session = Depends(get_db),
):
    validation_error = _validate_date_range(date_from, date_to)
    if validation_error:
        return validation_error

    summary = DashboardService.get_financial_summary(db, date_from=date_from, date_to=date_to)
    return success_response(
        message="Dashboard financial summary fetched successfully.",
        data={
            "total_income": _serialize_decimal(summary["total_income"]),
            "total_expense": _serialize_decimal(summary["total_expense"]),
            "profit_or_loss": _serialize_decimal(summary["profit_or_loss"]),
        },
    )


@router.get("/upcoming-events", response_model=ApiResponse)
def get_upcoming_events(db: Session = Depends(get_db)):
    events = DashboardService.get_upcoming_events(db, date.today())
    return success_response(
        message="Dashboard upcoming events fetched successfully.",
        data=[_serialize_event(event) for event in events],
    )


@router.get("/alerts", response_model=ApiResponse)
def get_dashboard_alerts(db: Session = Depends(get_db)):
    alerts = DashboardService.get_alerts(db, date.today())
    return success_response(
        message="Dashboard alerts fetched successfully.",
        data={
            "sick_animals": [_serialize_animal(animal) for animal in alerts["sick_animals"]],
            "upcoming_vaccinations": [_serialize_event(event) for event in alerts["upcoming_vaccinations"]],
            "upcoming_deworming": [_serialize_event(event) for event in alerts["upcoming_deworming"]],
            "milking_animals_without_milk_entry_today": [
                _serialize_animal(animal)
                for animal in alerts["milking_animals_without_milk_entry_today"]
            ],
        },
    )
