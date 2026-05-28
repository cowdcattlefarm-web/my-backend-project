from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.income_entry import IncomeEntryCreate, IncomeEntryRead, IncomeEntryUpdate, IncomeType, PaymentMode
from app.services.income_entry_service import IncomeEntryService
from app.utils.responses import error_response, success_response

router = APIRouter(prefix="/income")


def _serialize_income_entry(income_entry) -> dict:
    return IncomeEntryRead.model_validate(income_entry).model_dump(mode="json")


def _not_found_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response(message=message),
    )


def _bad_request_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response(message=message),
    )


def _validate_date_range(date_from: date | None, date_to: date | None) -> JSONResponse | None:
    if date_from is not None and date_to is not None and date_from > date_to:
        return _bad_request_response("date_from must be before or equal to date_to.")
    return None


def _validate_references(
    db: Session,
    *,
    animal_id: int | None,
    milk_entry_id: int | None,
) -> JSONResponse | None:
    if animal_id is not None and IncomeEntryService.get_animal(db, animal_id) is None:
        return _bad_request_response("Animal not found.")
    if milk_entry_id is not None and IncomeEntryService.get_milk_entry(db, milk_entry_id) is None:
        return _bad_request_response("Milk entry not found.")
    return None


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_income_entry(
    payload: IncomeEntryCreate,
    db: Session = Depends(get_db),
):
    validation_error = _validate_references(
        db,
        animal_id=payload.animal_id,
        milk_entry_id=payload.milk_entry_id,
    )
    if validation_error:
        return validation_error

    income_entry = IncomeEntryService.create_income_entry(db, payload)
    return success_response(
        message="Income entry created successfully.",
        data=_serialize_income_entry(income_entry),
    )


@router.get("", response_model=ApiResponse)
def list_income_entries(
    page: int = Query(default=1, ge=1, examples=[1]),
    limit: int = Query(default=10, ge=1, le=100, examples=[10]),
    income_type: IncomeType | None = Query(default=None),
    payment_mode: PaymentMode | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    validation_error = _validate_date_range(date_from, date_to)
    if validation_error:
        return validation_error

    income_entries, total, total_income_amount = IncomeEntryService.list_income_entries(
        db,
        page=page,
        limit=limit,
        income_type=income_type.value if income_type else None,
        payment_mode=payment_mode.value if payment_mode else None,
        date_from=date_from,
        date_to=date_to,
    )

    return success_response(
        message="Income entries fetched successfully.",
        data={
            "items": [_serialize_income_entry(income_entry) for income_entry in income_entries],
            "metadata": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_income_amount": str(total_income_amount),
            },
        },
    )


@router.get("/{income_id}", response_model=ApiResponse)
def get_income_entry(
    income_id: int,
    db: Session = Depends(get_db),
):
    income_entry = IncomeEntryService.get_income_entry(db, income_id)
    if income_entry is None:
        return _not_found_response("Income entry not found.")

    return success_response(
        message="Income entry fetched successfully.",
        data=_serialize_income_entry(income_entry),
    )


@router.put("/{income_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def update_income_entry(
    income_id: int,
    payload: IncomeEntryUpdate,
    db: Session = Depends(get_db),
):
    income_entry = IncomeEntryService.get_income_entry(db, income_id)
    if income_entry is None:
        return _not_found_response("Income entry not found.")

    animal_id = payload.animal_id if "animal_id" in payload.model_fields_set else income_entry.animal_id
    milk_entry_id = payload.milk_entry_id if "milk_entry_id" in payload.model_fields_set else income_entry.milk_entry_id

    validation_error = _validate_references(
        db,
        animal_id=animal_id,
        milk_entry_id=milk_entry_id,
    )
    if validation_error:
        return validation_error

    income_entry = IncomeEntryService.update_income_entry(db, income_entry, payload)
    return success_response(
        message="Income entry updated successfully.",
        data=_serialize_income_entry(income_entry),
    )


@router.delete("/{income_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def delete_income_entry(
    income_id: int,
    db: Session = Depends(get_db),
):
    income_entry = IncomeEntryService.get_income_entry(db, income_id)
    if income_entry is None:
        return _not_found_response("Income entry not found.")

    IncomeEntryService.delete_income_entry(db, income_entry)
    return success_response(
        message="Income entry deleted successfully.",
        data={"id": income_id},
    )
