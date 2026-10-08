import uuid
from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

SortField = Literal["spent_on", "amount", "created_at"]
SortDir = Literal["asc", "desc"]


def _assert_category_owned(db: Session, user_id: uuid.UUID, category_id: uuid.UUID) -> None:
    exists = db.execute(
        select(Category.id).where(Category.id == category_id, Category.user_id == user_id)
    ).scalar_one_or_none()
    if exists is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")


def create_expense(db: Session, user_id: uuid.UUID, data: ExpenseCreate) -> Expense:
    _assert_category_owned(db, user_id, data.category_id)

    expense = Expense(user_id=user_id, **data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_owned_expense(db: Session, user_id: uuid.UUID, expense_id: uuid.UUID) -> Expense:
    """404 (never 403) for an expense that doesn't exist or isn't the caller's."""
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    ).scalar_one_or_none()
    if expense is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Expense not found")
    return expense


def update_expense(
    db: Session, user_id: uuid.UUID, expense_id: uuid.UUID, data: ExpenseUpdate
) -> Expense:
    expense = get_owned_expense(db, user_id, expense_id)

    updates = data.model_dump(exclude_unset=True)
    if "category_id" in updates:
        _assert_category_owned(db, user_id, updates["category_id"])

    for field, value in updates.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, user_id: uuid.UUID, expense_id: uuid.UUID) -> None:
    expense = get_owned_expense(db, user_id, expense_id)
    db.delete(expense)
    db.commit()


def attach_receipt(
    db: Session, user_id: uuid.UUID, expense_id: uuid.UUID, receipt_key: str
) -> Expense:
    expense = get_owned_expense(db, user_id, expense_id)
    expense.receipt_key = receipt_key
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(
    db: Session,
    user_id: uuid.UUID,
    *,
    category_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    sort_by: SortField = "spent_on",
    sort_dir: SortDir = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Expense], int]:
    query = select(Expense).where(Expense.user_id == user_id)
    count_query = select(func.count()).select_from(Expense).where(Expense.user_id == user_id)

    if category_id is not None:
        query = query.where(Expense.category_id == category_id)
        count_query = count_query.where(Expense.category_id == category_id)
    if date_from is not None:
        query = query.where(Expense.spent_on >= date_from)
        count_query = count_query.where(Expense.spent_on >= date_from)
    if date_to is not None:
        query = query.where(Expense.spent_on <= date_to)
        count_query = count_query.where(Expense.spent_on <= date_to)
    if min_amount is not None:
        query = query.where(Expense.amount >= min_amount)
        count_query = count_query.where(Expense.amount >= min_amount)
    if max_amount is not None:
        query = query.where(Expense.amount <= max_amount)
        count_query = count_query.where(Expense.amount <= max_amount)

    sort_column = getattr(Expense, sort_by)
    query = query.order_by(sort_column.desc() if sort_dir == "desc" else sort_column.asc())
    query = query.limit(limit).offset(offset)

    total = db.execute(count_query).scalar_one()
    items = list(db.execute(query).scalars().all())
    return items, total
