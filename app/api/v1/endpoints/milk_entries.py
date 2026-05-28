from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.milk_entry import (
    AnimalMilkSummary,
    DailyMilkSummary,
    MilkEntryCreate,
    MilkEntryRead,
    MilkEntryUpdate,
    MilkShift,
    MonthlyMilkSummaryItem,
)
from app.services.milk_entry_service import MilkEntryService
from app.utils.responses import error_response, success_response

router = APIRouter(prefix="/milk-entries")


def _serialize_milk_entry(milk_entry) -> dict:
    return MilkEntryRead.model_validate(milk_entry).model_dump(mode="json")


def _not_found_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response(message=message),
    )


def _conflict_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response(message=message),
    )


def _bad_request_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response(message=message),
    )


def _validate_animal_for_entry(db: Session, animal_id: int) -> JSONResponse | None:
    animal = MilkEntryService.get_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")
    if not MilkEntryService.is_animal_milking(animal):
        return _bad_request_response("Milk entry is allowed only for animals with current_status 'milking'.")
    return None


def _validate_duplicate_entry(
    db: Session,
    *,
    animal_id: int,
    entry_date: date,
    shift: MilkShift | str,
    exclude_id: int | None = None,
) -> JSONResponse | None:
    shift_value = shift.value if isinstance(shift, MilkShift) else shift
    if MilkEntryService.duplicate_entry_exists(
        db,
        animal_id=animal_id,
        entry_date=entry_date,
        shift=shift_value,
        exclude_id=exclude_id,
    ):
        return _conflict_response("Milk entry already exists for this animal, date, and shift.")
    return None


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_milk_entry(
    payload: MilkEntryCreate,
    db: Session = Depends(get_db),
):
    animal_error = _validate_animal_for_entry(db, payload.animal_id)
    if animal_error:
        return animal_error

    duplicate_error = _validate_duplicate_entry(
        db,
        animal_id=payload.animal_id,
        entry_date=payload.entry_date,
        shift=payload.shift,
    )
    if duplicate_error:
        return duplicate_error

    milk_entry = MilkEntryService.create_milk_entry(db, payload)
    return success_response(
        message="Milk entry created successfully.",
        data=_serialize_milk_entry(milk_entry),
    )


@router.get("/daily-summary", response_model=ApiResponse)
def get_daily_summary(
    entry_date: date = Query(..., examples=["2026-05-14"]),
    db: Session = Depends(get_db),
):
    summary = DailyMilkSummary(
        entry_date=entry_date,
        total_quantity_liters=MilkEntryService.get_daily_summary(db, entry_date),
    )
    return success_response(
        message="Daily milk summary fetched successfully.",
        data=summary.model_dump(mode="json"),
    )


@router.get("/monthly-summary", response_model=ApiResponse)
def get_monthly_summary(
    year: int = Query(..., ge=1, examples=[2026]),
    month: int = Query(..., ge=1, le=12, examples=[5]),
    db: Session = Depends(get_db),
):
    items = [
        MonthlyMilkSummaryItem(entry_date=entry_date, total_quantity_liters=total_quantity_liters).model_dump(mode="json")
        for entry_date, total_quantity_liters in MilkEntryService.get_monthly_summary(db, year, month)
    ]
    return success_response(
        message="Monthly milk summary fetched successfully.",
        data={
            "year": year,
            "month": month,
            "items": items,
        },
    )


@router.get("/animal/{animal_id}/summary", response_model=ApiResponse)
def get_animal_summary(
    animal_id: int,
    db: Session = Depends(get_db),
):
    animal = MilkEntryService.get_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")

    total_quantity_liters, average_quantity_liters, entry_count = MilkEntryService.get_animal_summary(db, animal_id)
    summary = AnimalMilkSummary(
        animal_id=animal_id,
        total_quantity_liters=total_quantity_liters,
        average_quantity_liters=average_quantity_liters,
        entry_count=entry_count,
    )
    return success_response(
        message="Animal milk summary fetched successfully.",
        data=summary.model_dump(mode="json"),
    )


@router.get("", response_model=ApiResponse)
def list_milk_entries(
    animal_id: int | None = Query(default=None, ge=1),
    entry_date: date | None = Query(default=None),
    shift: MilkShift | None = Query(default=None),
    db: Session = Depends(get_db),
):
    milk_entries = MilkEntryService.list_milk_entries(
        db,
        animal_id=animal_id,
        entry_date=entry_date,
        shift=shift.value if shift else None,
    )
    return success_response(
        message="Milk entries fetched successfully.",
        data=[_serialize_milk_entry(milk_entry) for milk_entry in milk_entries],
    )


@router.get("/{milk_entry_id}", response_model=ApiResponse)
def get_milk_entry(
    milk_entry_id: int,
    db: Session = Depends(get_db),
):
    milk_entry = MilkEntryService.get_milk_entry(db, milk_entry_id)
    if milk_entry is None:
        return _not_found_response("Milk entry not found.")

    return success_response(
        message="Milk entry fetched successfully.",
        data=_serialize_milk_entry(milk_entry),
    )


@router.put("/{milk_entry_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def update_milk_entry(
    milk_entry_id: int,
    payload: MilkEntryUpdate,
    db: Session = Depends(get_db),
):
    milk_entry = MilkEntryService.get_milk_entry(db, milk_entry_id)
    if milk_entry is None:
        return _not_found_response("Milk entry not found.")

    animal_id = payload.animal_id if "animal_id" in payload.model_fields_set else milk_entry.animal_id
    entry_date = payload.entry_date if "entry_date" in payload.model_fields_set else milk_entry.entry_date
    shift = payload.shift if "shift" in payload.model_fields_set else milk_entry.shift

    animal_error = _validate_animal_for_entry(db, animal_id)
    if animal_error:
        return animal_error

    duplicate_error = _validate_duplicate_entry(
        db,
        animal_id=animal_id,
        entry_date=entry_date,
        shift=shift,
        exclude_id=milk_entry_id,
    )
    if duplicate_error:
        return duplicate_error

    milk_entry = MilkEntryService.update_milk_entry(db, milk_entry, payload)
    return success_response(
        message="Milk entry updated successfully.",
        data=_serialize_milk_entry(milk_entry),
    )


@router.delete("/{milk_entry_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def delete_milk_entry(
    milk_entry_id: int,
    db: Session = Depends(get_db),
):
    milk_entry = MilkEntryService.get_milk_entry(db, milk_entry_id)
    if milk_entry is None:
        return _not_found_response("Milk entry not found.")

    MilkEntryService.delete_milk_entry(db, milk_entry)
    return success_response(
        message="Milk entry deleted successfully.",
        data={"id": milk_entry_id},
    )
