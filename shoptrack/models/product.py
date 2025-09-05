from .base import BaseModel
from typing import Optional, List
from sqlalchemy import String, ForeignKey, CheckConstraint, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Product(BaseModel):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(String(1000))

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="products")
    history: Mapped[List['History']] = relationship(
        back_populates='product',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        CheckConstraint('price > 0.0', name='price_positive'),
        CheckConstraint('stock >= 0', name='stock_positive')
    )
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, stock={self.stock})>"