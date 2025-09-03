from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shoptrack.database import Base

class Product(Base):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(default=0)

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="products")

    __table_args__ = (
        CheckConstraint('price > 0.0', name='price_positive'),
        CheckConstraint('stock >= 0', name='stock_positive')
    )
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price}, stock={self.stock})>"