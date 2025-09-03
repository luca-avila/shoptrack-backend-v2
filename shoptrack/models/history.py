from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shoptrack.database import Base

class History(Base):
    __tablename__ = "history"

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product_name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    price: Mapped[float] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint('price > 0.0', name='price_positive'),
        CheckConstraint('quantity > 0', name='quantity_positive'),
        CheckConstraint('action IN ("buy", "sell")', name='action_valid')
    )
    def __repr__(self):
        return f"<History(id={self.id}, product_id={self.product_id}, product_name={self.product_name}, user_id={self.user_id}, price={self.price}, quantity={self.quantity}, action={self.action})>"