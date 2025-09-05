from .base import BaseModel
from typing import Optional
from sqlalchemy import String, ForeignKey, CheckConstraint, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

class History(BaseModel):
    __tablename__ = "history"

    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product.id"))
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(10), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="history")
    product: Mapped[Optional["Product"]] = relationship(back_populates="history")

    __table_args__ = (
        CheckConstraint('price > 0.0', name='price_positive'),
        CheckConstraint('quantity > 0', name='quantity_positive'),
        CheckConstraint('action IN ("buy", "sell")', name='action_valid')
    )
    def __repr__(self):
        return f"<History(id={self.id}, action='{self.action}', product='{self.product_name}', quantity={self.quantity})>"