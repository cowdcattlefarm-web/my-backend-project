from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MilkShift(StrEnum):
    morning = "morning"
    evening = "evening"
    other = "other"


class MilkEntryBase(BaseModel):
    animal_id: int = Field(..., ge=1, examples=[1])
    entry_date: date = Field(..., examples=["2026-05-14"])
    shift: MilkShift = Field(..., examples=["morning"])
    quantity_liters: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, examples=["12.50"])
    fat_percentage: Decimal | None = Field(default=None, max_digits=5, decimal_places=2, examples=["4.20"])
    snf_percentage: Decimal | None = Field(default=None, max_digits=5, decimal_places=2, examples=["8.60"])
    milk_quality_notes: str | None = Field(default=None, examples=["Normal consistency."])
    recorded_by: str | None = Field(default=None, max_length=255, examples=["Ramesh"])


class MilkEntryCreate(MilkEntryBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "animal_id": 1,
                "entry_date": "2026-05-14",
                "shift": "morning",
                "quantity_liters": "12.50",
                "fat_percentage": "4.20",
                "snf_percentage": "8.60",
                "milk_quality_notes": "Normal consistency.",
                "recorded_by": "Ramesh",
            }
        }
    )


class MilkEntryUpdate(BaseModel):
    animal_id: int | None = Field(default=None, ge=1, examples=[1])
    entry_date: date | None = Field(default=None, examples=["2026-05-14"])
    shift: MilkShift | None = Field(default=None, examples=["evening"])
    quantity_liters: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2, examples=["10.75"])
    fat_percentage: Decimal | None = Field(default=None, max_digits=5, decimal_places=2, examples=["4.10"])
    snf_percentage: Decimal | None = Field(default=None, max_digits=5, decimal_places=2, examples=["8.55"])
    milk_quality_notes: str | None = Field(default=None, examples=["Slightly lower volume."])
    recorded_by: str | None = Field(default=None, max_length=255, examples=["Suresh"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_liters": "10.75",
                "shift": "evening",
                "recorded_by": "Suresh",
            }
        }
    )


class MilkEntryRead(MilkEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyMilkSummary(BaseModel):
    entry_date: date
    total_quantity_liters: Decimal


class MonthlyMilkSummaryItem(BaseModel):
    entry_date: date
    total_quantity_liters: Decimal


class AnimalMilkSummary(BaseModel):
    animal_id: int
    total_quantity_liters: Decimal
    average_quantity_liters: Decimal
    entry_count: int
