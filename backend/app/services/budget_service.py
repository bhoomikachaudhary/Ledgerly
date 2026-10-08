import calendar
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.budget import (
    BudgetUpsert,
    CategorySummary,
    SummaryResponse,
    TrendPoint,
    TrendResponse,
)
from app.services.category_service import get_owned_category


def upsert_budget(db: Session, user_id: uuid.UUID, data: BudgetUpsert) -> Budget:
    get_owned_category(db, user_id, data.category_id)  # 404 if not owned

    existing = db.execute(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == data.category_id,
            Budget.month == data.month,
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.limit_amount = data.limit_amount
        db.commit()
        db.refresh(existing)
        return existing

    budget = Budget(user_id=user_id, **data.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session, user_id: uuid.UUID, month: str) -> list[Budget]:
    return list(
        db.execute(
            select(Budget).where(Budget.user_id == user_id, Budget.month == month)
        ).scalars().all()
    )


def _month_bounds(month: str) -> tuple[date, date]:
    year, mon = (int(part) for part in month.split("-"))
    last_day = calendar.monthrange(year, mon)[1]
    return date(year, mon, 1), date(year, mon, last_day)


def get_summary(db: Session, user_id: uuid.UUID, month: str) -> SummaryResponse:
    start, end = _month_bounds(month)

    spent_rows = db.execute(
        select(Expense.category_id, func.sum(Expense.amount))
        .where(
            Expense.user_id == user_id,
            Expense.spent_on >= start,
            Expense.spent_on <= end,
        )
        .group_by(Expense.category_id)
    ).all()
    spent_by_category: dict[uuid.UUID, Decimal] = {row[0]: row[1] for row in spent_rows}

    budgets = list_budgets(db, user_id, month)
    budget_by_category: dict[uuid.UUID, Decimal] = {b.category_id: b.limit_amount for b in budgets}

    category_ids = set(spent_by_category) | set(budget_by_category)
    categories_by_id: dict[uuid.UUID, Category] = {}
    if category_ids:
        rows = db.execute(select(Category).where(Category.id.in_(category_ids))).scalars().all()
        categories_by_id = {c.id: c for c in rows}

    summaries = [
        CategorySummary(
            category_id=cid,
            category_name=categories_by_id[cid].name if cid in categories_by_id else "Unknown",
            spent=spent_by_category.get(cid, Decimal("0.00")),
            budget=budget_by_category.get(cid),
        )
        for cid in category_ids
    ]
    summaries.sort(key=lambda s: s.category_name)

    return SummaryResponse(
        month=month,
        categories=summaries,
        total_spent=sum(spent_by_category.values(), Decimal("0.00")),
        total_budget=sum(budget_by_category.values(), Decimal("0.00")),
    )


def get_trend(db: Session, user_id: uuid.UUID, months_back: int = 6) -> TrendResponse:
    today = date.today()
    points: list[TrendPoint] = []

    year, mon = today.year, today.month
    for _ in range(months_back):
        month_str = f"{year:04d}-{mon:02d}"
        start, end = _month_bounds(month_str)

        total = db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                Expense.spent_on >= start,
                Expense.spent_on <= end,
            )
        ).scalar_one()
        points.append(TrendPoint(month=month_str, total_spent=Decimal(total)))

        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1

    points.reverse()
    return TrendResponse(months=points)
