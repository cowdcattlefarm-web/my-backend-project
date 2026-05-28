from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.expense_entry import ExpenseEntryCreate, ExpenseEntryRead, ExpenseEntryUpdate, ExpenseType, PaymentMode
from app.services.expense_entry_service import ExpenseEntryService
from app.utils.responses import error_response, success_response

router = APIRouter(prefix="/expenses")


def _serialize_expense_entry(expense_entry) -> dict:
    return ExpenseEntryRead.model_validate(expense_entry).model_dump(mode="json")


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
    animal_event_id: int | None,
) -> JSONResponse | None:
    if animal_id is not None and ExpenseEntryService.get_animal(db, animal_id) is None:
        return _bad_request_response("Animal not found.")
    if animal_event_id is not None and ExpenseEntryService.get_animal_event(db, animal_event_id) is None:
        return _bad_request_response("Animal event not found.")
    return None


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_expense_entry(
    payload: ExpenseEntryCreate,
    db: Session = Depends(get_db),
):
    validation_error = _validate_references(
        db,
        animal_id=payload.animal_id,
        animal_event_id=payload.animal_event_id,
    )
    if validation_error:
        return validation_error

    expense_entry = ExpenseEntryService.create_expense_entry(db, payload)
    return success_response(
        message="Expense entry created successfully.",
        data=_serialize_expense_entry(expense_entry),
    )


@router.get("", response_model=ApiResponse)
def list_expense_entries(
    page: int = Query(default=1, ge=1, examples=[1]),
    limit: int = Query(default=10, ge=1, le=100, examples=[10]),
    expense_type: ExpenseType | None = Query(default=None),
    payment_mode: PaymentMode | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    validation_error = _validate_date_range(date_from, date_to)
    if validation_error:
        return validation_error

    expense_entries, total, total_expense_amount = ExpenseEntryService.list_expense_entries(
        db,
        page=page,
        limit=limit,
        expense_type=expense_type.value if expense_type else None,
        payment_mode=payment_mode.value if payment_mode else None,
        date_from=date_from,
        date_to=date_to,
    )

    return success_response(
        message="Expense entries fetched successfully.",
        data={
            "items": [_serialize_expense_entry(expense_entry) for expense_entry in expense_entries],
            "metadata": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_expense_amount": str(total_expense_amount),
            },
        },
    )


@router.get("/{expense_id}", response_model=ApiResponse)
def get_expense_entry(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense_entry = ExpenseEntryService.get_expense_entry(db, expense_id)
    if expense_entry is None:
        return _not_found_response("Expense entry not found.")

    return success_response(
        message="Expense entry fetched successfully.",
        data=_serialize_expense_entry(expense_entry),
    )


@router.put("/{expense_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def update_expense_entry(
    expense_id: int,
    payload: ExpenseEntryUpdate,
    db: Session = Depends(get_db),
):
    expense_entry = ExpenseEntryService.get_expense_entry(db, expense_id)
    if expense_entry is None:
        return _not_found_response("Expense entry not found.")

    animal_id = payload.animal_id if "animal_id" in payload.model_fields_set else expense_entry.animal_id
    animal_event_id = (
        payload.animal_event_id if "animal_event_id" in payload.model_fields_set else expense_entry.animal_event_id
    )

    validation_error = _validate_references(
        db,
        animal_id=animal_id,
        animal_event_id=animal_event_id,
    )
    if validation_error:
        return validation_error

    expense_entry = ExpenseEntryService.update_expense_entry(db, expense_entry, payload)
    return success_response(
        message="Expense entry updated successfully.",
        data=_serialize_expense_entry(expense_entry),
    )


@router.delete("/{expense_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def delete_expense_entry(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense_entry = ExpenseEntryService.get_expense_entry(db, expense_id)
    if expense_entry is None:
        return _not_found_response("Expense entry not found.")

    ExpenseEntryService.delete_expense_entry(db, expense_entry)
    return success_response(
        message="Expense entry deleted successfully.",
        data={"id": expense_id},
    )
