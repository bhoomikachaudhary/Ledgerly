import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    category_id: uuid.UUID
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    spent_on: date
    note: Optional[str] = Field(default=None, max_length=500)


class ExpenseUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    amount: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2, max_digits=12)
    spent_on: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=500)


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    amount: Decimal
    spent_on: date
    note: Optional[str]
    receipt_key: Optional[str]
    created_at: datetime


class ExpenseListResponse(BaseModel):
    items: list[ExpenseOut]
    total: int
    limit: int
    offset: int
