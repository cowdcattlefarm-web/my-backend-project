from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ExpenseType(StrEnum):
    feed = "feed"
    fodder = "fodder"
    medicine = "medicine"
    vet_visit = "vet_visit"
    vaccination = "vaccination"
    deworming = "deworming"
    labour = "labour"
    electricity = "electricity"
    water = "water"
    transport = "transport"
    equipment = "equipment"
    maintenance = "maintenance"
    animal_purchase = "animal_purchase"
    rent = "rent"
    loan = "loan"
    other = "other"


class PaymentMode(StrEnum):
    cash = "cash"
    upi = "upi"
    bank_transfer = "bank_transfer"
    card = "card"
    cheque = "cheque"
    other = "other"


class ExpenseEntryBase(BaseModel):
    expense_date: date = Field(..., examples=["2026-05-14"])
    expense_type: ExpenseType = Field(..., examples=["feed"])
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, examples=["1250.00"])
    payment_mode: PaymentMode = Field(..., examples=["upi"])
    vendor_name: str | None = Field(default=None, max_length=255, examples=["Local Feed Supplier"])
    description: str | None = Field(default=None, examples=["Monthly cattle feed purchase."])
    animal_id: int | None = Field(default=None, ge=1, examples=[1])
    animal_event_id: int | None = Field(default=None, ge=1, examples=[1])


class ExpenseEntryCreate(ExpenseEntryBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "expense_date": "2026-05-14",
                "expense_type": "feed",
                "amount": "1250.00",
                "payment_mode": "upi",
                "vendor_name": "Local Feed Supplier",
                "description": "Monthly cattle feed purchase.",
                "animal_id": 1,
                "animal_event_id": 1,
            }
        }
    )


class ExpenseEntryUpdate(BaseModel):
    expense_date: date | None = Field(default=None, examples=["2026-05-14"])
    expense_type: ExpenseType | None = Field(default=None, examples=["medicine"])
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2, examples=["1500.00"])
    payment_mode: PaymentMode | None = Field(default=None, examples=["bank_transfer"])
    vendor_name: str | None = Field(default=None, max_length=255, examples=["Updated Vendor"])
    description: str | None = Field(default=None, examples=["Updated expense details."])
    animal_id: int | None = Field(default=None, ge=1, examples=[1])
    animal_event_id: int | None = Field(default=None, ge=1, examples=[1])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": "1500.00",
                "payment_mode": "bank_transfer",
                "vendor_name": "Updated Vendor",
            }
        }
    )


class ExpenseEntryRead(ExpenseEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
