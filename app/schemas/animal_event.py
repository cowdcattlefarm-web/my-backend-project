from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AnimalEventType(StrEnum):
    birth = "birth"
    purchase = "purchase"
    vaccination = "vaccination"
    deworming = "deworming"
    disease = "disease"
    treatment = "treatment"
    medicine = "medicine"
    vet_visit = "vet_visit"
    weight_check = "weight_check"
    heat_detected = "heat_detected"
    artificial_insemination = "artificial_insemination"
    natural_breeding = "natural_breeding"
    pregnancy_check = "pregnancy_check"
    pregnancy_confirmed = "pregnancy_confirmed"
    pregnancy_failed = "pregnancy_failed"
    abortion = "abortion"
    calving = "calving"
    dry_off = "dry_off"
    lactation_start = "lactation_start"
    lactation_end = "lactation_end"
    milk_yield_issue = "milk_yield_issue"
    hoof_trimming = "hoof_trimming"
    injury = "injury"
    feed_change = "feed_change"
    body_condition_score = "body_condition_score"
    sale = "sale"
    death = "death"
    culling = "culling"
    transfer = "transfer"
    general_note = "general_note"


class AnimalEventBase(BaseModel):
    event_type: AnimalEventType = Field(..., examples=["vaccination"])
    event_date: date = Field(..., examples=["2026-05-14"])
    title: str = Field(..., max_length=255, examples=["FMD vaccination"])
    description: str | None = Field(default=None, examples=["Routine preventive vaccination."])
    performed_by: str | None = Field(default=None, max_length=255, examples=["Farm supervisor"])
    vet_name: str | None = Field(default=None, max_length=255, examples=["Dr. Sharma"])
    medicine_name: str | None = Field(default=None, max_length=255, examples=["FMD vaccine"])
    dosage: str | None = Field(default=None, max_length=255, examples=["2 ml"])
    cost: Decimal | None = Field(default=None, max_digits=10, decimal_places=2, examples=["450.00"])
    next_due_date: date | None = Field(default=None, examples=["2026-11-14"])
    attachment_url: str | None = Field(default=None, max_length=500, examples=["https://example.com/reports/vaccine.pdf"])


class AnimalEventCreate(AnimalEventBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "vaccination",
                "event_date": "2026-05-14",
                "title": "FMD vaccination",
                "description": "Routine preventive vaccination.",
                "performed_by": "Farm supervisor",
                "vet_name": "Dr. Sharma",
                "medicine_name": "FMD vaccine",
                "dosage": "2 ml",
                "cost": "450.00",
                "next_due_date": "2026-11-14",
                "attachment_url": "https://example.com/reports/vaccine.pdf",
            }
        }
    )


class AnimalEventUpdate(BaseModel):
    event_type: AnimalEventType | None = Field(default=None, examples=["treatment"])
    event_date: date | None = Field(default=None, examples=["2026-05-15"])
    title: str | None = Field(default=None, max_length=255, examples=["Follow-up treatment"])
    description: str | None = Field(default=None, examples=["Updated treatment notes."])
    performed_by: str | None = Field(default=None, max_length=255, examples=["Farm supervisor"])
    vet_name: str | None = Field(default=None, max_length=255, examples=["Dr. Sharma"])
    medicine_name: str | None = Field(default=None, max_length=255, examples=["Antibiotic"])
    dosage: str | None = Field(default=None, max_length=255, examples=["5 ml"])
    cost: Decimal | None = Field(default=None, max_digits=10, decimal_places=2, examples=["650.00"])
    next_due_date: date | None = Field(default=None, examples=["2026-05-22"])
    attachment_url: str | None = Field(default=None, max_length=500, examples=["https://example.com/reports/treatment.pdf"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "treatment",
                "title": "Follow-up treatment",
                "cost": "650.00",
                "next_due_date": "2026-05-22",
            }
        }
    )


class AnimalEventRead(AnimalEventBase):
    id: int
    animal_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "animal_id": 1,
                "event_type": "vaccination",
                "event_date": "2026-05-14",
                "title": "FMD vaccination",
                "description": "Routine preventive vaccination.",
                "performed_by": "Farm supervisor",
                "vet_name": "Dr. Sharma",
                "medicine_name": "FMD vaccine",
                "dosage": "2 ml",
                "cost": "450.00",
                "next_due_date": "2026-11-14",
                "attachment_url": "https://example.com/reports/vaccine.pdf",
                "created_at": "2026-05-14T12:00:00Z",
                "updated_at": "2026-05-14T12:00:00Z",
            }
        },
    )
