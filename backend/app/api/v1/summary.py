from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.budget import MONTH_PATTERN, SummaryResponse, TrendResponse
from app.services import budget_service

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", response_model=SummaryResponse)
def get_summary(
    month: str = Query(..., pattern=MONTH_PATTERN.pattern, description="YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    return budget_service.get_summary(db, current_user.id, month)


@router.get("/trend", response_model=TrendResponse)
def get_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrendResponse:
    return budget_service.get_trend(db, current_user.id)
