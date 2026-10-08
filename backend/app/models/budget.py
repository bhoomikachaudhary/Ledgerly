import uuid

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", name="uq_budgets_user_category_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    month: Mapped[str] = mapped_column(String(7), nullable=False)  # "YYYY-MM"
    limit_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
