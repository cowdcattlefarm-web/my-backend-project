from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.schemas.animal import AnimalCreate, AnimalRead, AnimalStatus, AnimalType, AnimalUpdate
from app.schemas.common import ApiResponse
from app.services.animal_service import AnimalService
from app.utils.responses import error_response, success_response

router = APIRouter(prefix="/animals")


def _serialize_animal(animal) -> dict:
    return AnimalRead.model_validate(animal).model_dump(mode="json")


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


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_animal(
    payload: AnimalCreate,
    db: Session = Depends(get_db),
):
    if AnimalService.animal_code_exists(db, payload.animal_code):
        return _conflict_response("Animal code already exists.")

    if payload.tag_number and AnimalService.tag_number_exists(db, payload.tag_number):
        return _conflict_response("Tag number already exists.")

    parent_error = AnimalService.validate_parent_ids(db, payload.mother_id, payload.father_id)
    if parent_error:
        return _bad_request_response(parent_error)

    animal = AnimalService.create_animal(db, payload)
    return success_response(
        message="Animal created successfully.",
        data=_serialize_animal(animal),
    )


@router.get("", response_model=ApiResponse)
def list_animals(
    page: int = Query(default=1, ge=1, examples=[1]),
    limit: int = Query(default=10, ge=1, le=100, examples=[10]),
    search: str | None = Query(default=None, examples=["ANM-001"]),
    animal_type: AnimalType | None = Query(default=None),
    current_status: AnimalStatus | None = Query(default=None),
    breed: str | None = Query(default=None, examples=["Holstein Friesian"]),
    db: Session = Depends(get_db),
):
    animals, total = AnimalService.list_animals(
        db,
        page=page,
        limit=limit,
        search=search,
        animal_type=animal_type.value if animal_type else None,
        current_status=current_status.value if current_status else None,
        breed=breed,
    )

    return success_response(
        message="Animals fetched successfully.",
        data={
            "items": [_serialize_animal(animal) for animal in animals],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
            },
        },
    )


@router.get("/{animal_id}", response_model=ApiResponse)
def get_animal(
    animal_id: int,
    db: Session = Depends(get_db),
):
    animal = AnimalService.get_active_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")

    return success_response(
        message="Animal fetched successfully.",
        data=_serialize_animal(animal),
    )


@router.put("/{animal_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def update_animal(
    animal_id: int,
    payload: AnimalUpdate,
    db: Session = Depends(get_db),
):
    animal = AnimalService.get_active_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")

    if payload.animal_code and AnimalService.animal_code_exists(db, payload.animal_code, exclude_id=animal_id):
        return _conflict_response("Animal code already exists.")

    if payload.tag_number and AnimalService.tag_number_exists(db, payload.tag_number, exclude_id=animal_id):
        return _conflict_response("Tag number already exists.")

    mother_id = payload.mother_id if "mother_id" in payload.model_fields_set else animal.mother_id
    father_id = payload.father_id if "father_id" in payload.model_fields_set else animal.father_id
    parent_error = AnimalService.validate_parent_ids(db, mother_id, father_id, animal_id=animal_id)
    if parent_error:
        return _bad_request_response(parent_error)

    animal = AnimalService.update_animal(db, animal, payload)
    return success_response(
        message="Animal updated successfully.",
        data=_serialize_animal(animal),
    )


@router.delete("/{animal_id}", response_model=ApiResponse, dependencies=[Depends(get_current_user)])
def delete_animal(
    animal_id: int,
    db: Session = Depends(get_db),
):
    animal = AnimalService.get_active_animal(db, animal_id)
    if animal is None:
        return _not_found_response("Animal not found.")

    AnimalService.soft_delete_animal(db, animal)
    return success_response(
        message="Animal deleted successfully.",
        data={"id": animal_id, "is_active": False},
    )
