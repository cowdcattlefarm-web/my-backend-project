from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.animal import Animal
from app.models.animal_event import AnimalEvent
from app.schemas.animal_event import (
    AnimalEventCreate,
    AnimalEventRead,
    AnimalEventType,
    AnimalEventUpdate,
)
from app.schemas.common import ApiResponse
from app.utils.responses import error_response, success_response

router = APIRouter()

EVENT_STATUS_MAP: dict[AnimalEventType, str] = {
    AnimalEventType.sale: "sold",
    AnimalEventType.death: "dead",
    AnimalEventType.culling: "culled",
    AnimalEventType.dry_off: "dry",
    AnimalEventType.lactation_start: "milking",
    AnimalEventType.pregnancy_confirmed: "pregnant",
}


def _serialize_event(event: AnimalEvent) -> dict:
    return AnimalEventRead.model_validate(event).model_dump(mode="json")


def _not_found_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response(message=message),
    )


def _apply_animal_status(animal: Animal, event_type: AnimalEventType | str) -> None:
    mapped_status = EVENT_STATUS_MAP.get(AnimalEventType(event_type))
    if mapped_status:
        animal.current_status = mapped_status


def _get_animal(db: Session, animal_id: int) -> Animal | None:
    return db.get(Animal, animal_id)


def _get_event(db: Session, event_id: int) -> AnimalEvent | None:
    return db.get(AnimalEvent, event_id)


def _event_query(
    animal_id: int | None = None,
    event_type: AnimalEventType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Select[tuple[AnimalEvent]]:
    query = select(AnimalEvent)

    if animal_id is not None:
        query = query.where(AnimalEvent.animal_id == animal_id)
    if event_type is not None:
        query = query.where(AnimalEvent.event_type == event_type.value)
    if date_from is not None:
        query = query.where(AnimalEvent.event_date >= date_from)
    if date_to is not None:
        query = query.where(AnimalEvent.event_date <= date_to)

    return query.order_by(AnimalEvent.event_date.desc(), AnimalEvent.id.desc())


@router.post(
    "/animals/{animal_id}/events",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_animal_event(
    animal_id: int,
    payload: AnimalEventCreate,
    db: Session = Depends(get_db),
):
    animal = _get_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")

    event = AnimalEvent(animal_id=animal_id, **payload.model_dump(mode="python"))
    db.add(event)
    _apply_animal_status(animal, payload.event_type)
    db.commit()
    db.refresh(event)

    return success_response(
        message="Animal event created successfully.",
        data=_serialize_event(event),
    )


@router.get("/animals/{animal_id}/events", response_model=ApiResponse)
def list_animal_events(
    animal_id: int,
    db: Session = Depends(get_db),
):
    animal = _get_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")

    events = db.scalars(_event_query(animal_id=animal_id)).all()
    return success_response(
        message="Animal events fetched successfully.",
        data=[_serialize_event(event) for event in events],
    )


@router.get("/animal-events", response_model=ApiResponse)
def list_all_animal_events(
    animal_id: int | None = Query(default=None),
    event_type: AnimalEventType | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    events = db.scalars(
        _event_query(
            animal_id=animal_id,
            event_type=event_type,
            date_from=date_from,
            date_to=date_to,
        )
    ).all()
    return success_response(
        message="Animal events fetched successfully.",
        data=[_serialize_event(event) for event in events],
    )


@router.get("/animal-events/{event_id}", response_model=ApiResponse)
def get_animal_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = _get_event(db, event_id)
    if event is None:
        return _not_found_response("Animal event not found.")

    return success_response(
        message="Animal event fetched successfully.",
        data=_serialize_event(event),
    )


@router.put("/animal-events/{event_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def update_animal_event(
    event_id: int,
    payload: AnimalEventUpdate,
    db: Session = Depends(get_db),
):
    event = _get_event(db, event_id)
    if event is None:
        return _not_found_response("Animal event not found.")

    updates = payload.model_dump(mode="python", exclude_unset=True)
    for field, value in updates.items():
        setattr(event, field, value)

    if "event_type" in updates:
        animal = _get_animal(db, event.animal_id)
        if animal is not None:
            _apply_animal_status(animal, updates["event_type"])

    db.commit()
    db.refresh(event)

    return success_response(
        message="Animal event updated successfully.",
        data=_serialize_event(event),
    )


@router.delete("/animal-events/{event_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def delete_animal_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = _get_event(db, event_id)
    if event is None:
        return _not_found_response("Animal event not found.")

    db.delete(event)
    db.commit()

    return success_response(
        message="Animal event deleted successfully.",
        data={"id": event_id},
    )
