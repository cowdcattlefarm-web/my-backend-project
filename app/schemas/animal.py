from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AnimalType(StrEnum):
    cow = "cow"
    buffalo = "buffalo"
    calf = "calf"
    heifer = "heifer"
    bull = "bull"
    ox = "ox"


class AnimalGender(StrEnum):
    female = "female"
    male = "male"


class AnimalStatus(StrEnum):
    calf = "calf"
    heifer = "heifer"
    milking = "milking"
    pregnant = "pregnant"
    dry = "dry"
    sick = "sick"
    sold = "sold"
    dead = "dead"
    culled = "culled"
    inactive = "inactive"


class AnimalBase(BaseModel):
    animal_code: str = Field(
        ...,
        max_length=50,
        examples=["ANM-001"],
    )
    tag_number: str | None = Field(
        default=None,
        max_length=50,
        examples=["TAG-001"],
    )
    name: str | None = Field(
        default=None,
        max_length=255,
        examples=["Gauri"],
    )
    animal_type: AnimalType = Field(
        ...,
        examples=["cow"],
    )
    breed: str | None = Field(
        default=None,
        max_length=100,
        examples=["Holstein Friesian"],
    )
    gender: AnimalGender = Field(
        ...,
        examples=["female"],
    )
    date_of_birth: date | None = Field(
        default=None,
        examples=["2023-06-15"],
    )
    color: str | None = Field(
        default=None,
        max_length=100,
        examples=["Black and White"],
    )
    purchase_date: date | None = Field(
        default=None,
        examples=["2024-01-20"],
    )
    purchase_price: Decimal | None = Field(
        default=None,
        decimal_places=2,
        examples=["85000.00"],
    )
    source: str | None = Field(
        default=None,
        max_length=255,
        examples=["Local breeder"],
    )
    current_status: AnimalStatus = Field(
        ...,
        examples=["milking"],
    )
    lactation_number: int | None = Field(
        default=None,
        ge=0,
        examples=[2],
    )
    mother_id: int | None = Field(
        default=None,
        ge=1,
        examples=[12],
    )
    father_id: int | None = Field(
        default=None,
        ge=1,
        examples=[18],
    )
    notes: str | None = Field(
        default=None,
        examples=["Healthy and regular milker."],
    )
    photo_url: str | None = Field(
        default=None,
        max_length=500,
        examples=["https://example.com/photos/anm-001.jpg"],
    )
    is_active: bool = Field(
        default=True,
        examples=[True],
    )


class AnimalCreate(AnimalBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "animal_code": "ANM-001",
                "tag_number": "TAG-001",
                "name": "Gauri",
                "animal_type": "cow",
                "breed": "Holstein Friesian",
                "gender": "female",
                "date_of_birth": "2023-06-15",
                "color": "Black and White",
                "purchase_date": "2024-01-20",
                "purchase_price": "85000.00",
                "source": "Local breeder",
                "current_status": "milking",
                "lactation_number": 2,
                "mother_id": 12,
                "father_id": 18,
                "notes": "Healthy and regular milker.",
                "photo_url": "https://example.com/photos/anm-001.jpg",
                "is_active": True,
            }
        }
    )


class AnimalUpdate(BaseModel):
    animal_code: str | None = Field(default=None, max_length=50, examples=["ANM-001"])
    tag_number: str | None = Field(default=None, max_length=50, examples=["TAG-001"])
    name: str | None = Field(default=None, max_length=255, examples=["Gauri"])
    animal_type: AnimalType | None = Field(default=None, examples=["cow"])
    breed: str | None = Field(default=None, max_length=100, examples=["Holstein Friesian"])
    gender: AnimalGender | None = Field(default=None, examples=["female"])
    date_of_birth: date | None = Field(default=None, examples=["2023-06-15"])
    color: str | None = Field(default=None, max_length=100, examples=["Black and White"])
    purchase_date: date | None = Field(default=None, examples=["2024-01-20"])
    purchase_price: Decimal | None = Field(default=None, decimal_places=2, examples=["85000.00"])
    source: str | None = Field(default=None, max_length=255, examples=["Local breeder"])
    current_status: AnimalStatus | None = Field(default=None, examples=["dry"])
    lactation_number: int | None = Field(default=None, ge=0, examples=[3])
    mother_id: int | None = Field(default=None, ge=1, examples=[12])
    father_id: int | None = Field(default=None, ge=1, examples=[18])
    notes: str | None = Field(default=None, examples=["Recently dried off."])
    photo_url: str | None = Field(default=None, max_length=500, examples=["https://example.com/photos/anm-001.jpg"])
    is_active: bool | None = Field(default=None, examples=[True])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_status": "dry",
                "lactation_number": 3,
                "notes": "Recently dried off.",
            }
        }
    )


class AnimalRead(AnimalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "animal_code": "ANM-001",
                "tag_number": "TAG-001",
                "name": "Gauri",
                "animal_type": "cow",
                "breed": "Holstein Friesian",
                "gender": "female",
                "date_of_birth": "2023-06-15",
                "color": "Black and White",
                "purchase_date": "2024-01-20",
                "purchase_price": "85000.00",
                "source": "Local breeder",
                "current_status": "milking",
                "lactation_number": 2,
                "mother_id": 12,
                "father_id": 18,
                "notes": "Healthy and regular milker.",
                "photo_url": "https://example.com/photos/anm-001.jpg",
                "is_active": True,
                "created_at": "2026-05-14T12:00:00Z",
                "updated_at": "2026-05-14T12:00:00Z",
            }
        },
    )
