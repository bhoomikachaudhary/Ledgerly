import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate


def list_categories(db: Session, user_id: uuid.UUID) -> list[Category]:
    return list(
        db.execute(select(Category).where(Category.user_id == user_id).order_by(Category.name))
        .scalars()
        .all()
    )


def create_category(db: Session, user_id: uuid.UUID, data: CategoryCreate) -> Category:
    category = Category(user_id=user_id, **data.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "You already have a category with this name"
        ) from exc
    db.refresh(category)
    return category


def get_owned_category(db: Session, user_id: uuid.UUID, category_id: uuid.UUID) -> Category:
    """Load a category the user owns, or 404 — never leak whether it belongs to someone else."""
    category = db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    ).scalar_one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return category
