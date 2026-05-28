from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class IncomeType(StrEnum):
    milk_sale = "milk_sale"
    animal_sale = "animal_sale"
    manure_sale = "manure_sale"
    product_sale = "product_sale"
    other = "other"


class PaymentMode(StrEnum):
    cash = "cash"
    upi = "upi"
    bank_transfer = "bank_transfer"
    card = "card"
    cheque = "cheque"
    other = "other"


class IncomeEntryBase(BaseModel):
    income_date: date = Field(..., examples=["2026-05-14"])
    income_type: IncomeType = Field(..., examples=["milk_sale"])
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, examples=["1250.00"])
    payment_mode: PaymentMode = Field(..., examples=["upi"])
    reference_number: str | None = Field(default=None, max_length=100, examples=["TXN-12345"])
    description: str | None = Field(default=None, examples=["Milk sold to local dairy buyer."])
    animal_id: int | None = Field(default=None, ge=1, examples=[1])
    milk_entry_id: int | None = Field(default=None, ge=1, examples=[1])


class IncomeEntryCreate(IncomeEntryBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "income_date": "2026-05-14",
                "income_type": "milk_sale",
                "amount": "1250.00",
                "payment_mode": "upi",
                "reference_number": "TXN-12345",
                "description": "Milk sold to local dairy buyer.",
                "animal_id": 1,
                "milk_entry_id": 1,
            }
        }
    )


class IncomeEntryUpdate(BaseModel):
    income_date: date | None = Field(default=None, examples=["2026-05-14"])
    income_type: IncomeType | None = Field(default=None, examples=["product_sale"])
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2, examples=["1500.00"])
    payment_mode: PaymentMode | None = Field(default=None, examples=["bank_transfer"])
    reference_number: str | None = Field(default=None, max_length=100, examples=["REF-9001"])
    description: str | None = Field(default=None, examples=["Updated income details."])
    animal_id: int | None = Field(default=None, ge=1, examples=[1])
    milk_entry_id: int | None = Field(default=None, ge=1, examples=[1])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": "1500.00",
                "payment_mode": "bank_transfer",
                "reference_number": "REF-9001",
            }
        }
    )


class IncomeEntryRead(IncomeEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
