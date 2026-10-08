import re
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class BudgetUpsert(BaseModel):
    category_id: uuid.UUID
    month: str = Field(description="YYYY-MM")
    limit_amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)

    @field_validator("month")
    @classmethod
    def validate_month(cls, value: str) -> str:
        if not MONTH_PATTERN.match(value):
            raise ValueError("month must be in YYYY-MM format")
        return value


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    month: str
    limit_amount: Decimal


class CategorySummary(BaseModel):
    category_id: uuid.UUID
    category_name: str
    spent: Decimal
    budget: Optional[Decimal]


class SummaryResponse(BaseModel):
    month: str
    categories: list[CategorySummary]
    total_spent: Decimal
    total_budget: Decimal


class TrendPoint(BaseModel):
    month: str
    total_spent: Decimal


class TrendResponse(BaseModel):
    months: list[TrendPoint]
