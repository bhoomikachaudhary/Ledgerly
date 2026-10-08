from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.budget import MONTH_PATTERN, BudgetOut, BudgetUpsert
from app.services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetOut])
def list_budgets(
    month: str = Query(..., pattern=MONTH_PATTERN.pattern, description="YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BudgetOut]:
    budgets = budget_service.list_budgets(db, current_user.id, month)
    return [BudgetOut.model_validate(b) for b in budgets]


@router.put("", response_model=BudgetOut)
def upsert_budget(
    data: BudgetUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetOut:
    budget = budget_service.upsert_budget(db, current_user.id, data)
    return BudgetOut.model_validate(budget)
