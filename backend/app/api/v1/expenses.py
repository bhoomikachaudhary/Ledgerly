import csv
import io
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseListResponse, ExpenseOut, ExpenseUpdate
from app.services import category_service, expense_service, storage_service
from app.services.expense_service import SortDir, SortField

router = APIRouter(prefix="/expenses", tags=["expenses"])


# NOTE: /export must be registered before /{expense_id} — otherwise FastAPI tries to
# parse "export" as a UUID path param and returns 422 instead of matching this route.
@router.get("/export")
def export_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    items, _ = expense_service.list_expenses(
        db, current_user.id, limit=10_000, offset=0, sort_by="spent_on", sort_dir="asc"
    )
    categories = {c.id: c.name for c in category_service.list_categories(db, current_user.id)}

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["date", "amount", "category", "note"])
    for expense in items:
        writer.writerow(
            [
                # Leading apostrophe forces Excel to treat this as text, not a date it
                # then reformats/garbles — this is the fix for the "####" column issue.
                f"'{expense.spent_on.isoformat()}",
                expense.amount,
                categories.get(expense.category_id, "Unknown"),
                expense.note or "",
            ]
        )
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )


@router.get("", response_model=ExpenseListResponse)
def list_expenses(
    category_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    sort_by: SortField = "spent_on",
    sort_dir: SortDir = "desc",
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseListResponse:
    items, total = expense_service.list_expenses(
        db,
        current_user.id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
    return ExpenseListResponse(
        items=[ExpenseOut.model_validate(e) for e in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    expense = expense_service.create_expense(db, current_user.id, data)
    return ExpenseOut.model_validate(expense)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    expense = expense_service.get_owned_expense(db, current_user.id, expense_id)
    return ExpenseOut.model_validate(expense)


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: uuid.UUID,
    data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    expense = expense_service.update_expense(db, current_user.id, expense_id, data)
    return ExpenseOut.model_validate(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    expense_service.delete_expense(db, current_user.id, expense_id)


@router.post("/{expense_id}/receipt", response_model=ExpenseOut)
def upload_receipt(
    expense_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    # Confirms ownership (404 if not the caller's) before touching storage.
    expense_service.get_owned_expense(db, current_user.id, expense_id)
    receipt_key = storage_service.save_receipt(file, current_user.id, expense_id)
    expense = expense_service.attach_receipt(db, current_user.id, expense_id, receipt_key)
    return ExpenseOut.model_validate(expense)