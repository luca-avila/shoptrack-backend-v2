from .base import BaseRepository
from ..models.product import Product
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    def get_with_owner(self, product_id: int) -> Optional[Product]:
        """Fetch a product and eagerly load its owner"""
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(joinedload(Product.owner))
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def find_by_name(self, name: str) -> Optional[Product]:
        """Find product by name"""
        return self.get_by(name=name)

    def find_all_by_owner(self, owner_id: int) -> List[Product]:
        """All products belonging to a given owner"""
        stmt = select(Product).where(Product.owner_id == owner_id)
        return self.session.execute(stmt).scalars().all()

    def find_low_stock(self, threshold: int) -> List[Product]:
        """All products with stock below threshold"""
        stmt = select(Product).where(Product.stock < threshold)
        return self.session.execute(stmt).scalars().all()
