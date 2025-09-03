from .base import BaseRepository
from ..models.history import History
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class HistoryRepository(BaseRepository[History]):
    def __init__(self, session):
        super().__init__(History, session)

    def get_with_user(self, history_id: int) -> Optional[History]:
        """Fetch history record with user loaded"""
        stmt = (
            select(History)
            .where(History.id == history_id)
            .options(joinedload(History.user))
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_with_product(self, history_id: int) -> Optional[History]:
        """Fetch history record with product loaded"""
        stmt = (
            select(History)
            .where(History.id == history_id)
            .options(joinedload(History.product))
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_with_user_and_product(self, history_id: int) -> Optional[History]:
        """Fetch history record with both user and product loaded"""
        stmt = (
            select(History)
            .where(History.id == history_id)
            .options(
                joinedload(History.user),
                joinedload(History.product)
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def find_by_user(self, user_id: int) -> List[History]:
        """Get all history records for a specific user"""
        return self.filter_by(user_id=user_id)

    def find_by_product(self, product_id: int) -> List[History]:
        """Get all history records for a specific product"""
        return self.filter_by(product_id=product_id)

    def find_by_action(self, action: str) -> List[History]:
        """Get all history records for a specific action (buy/sell)"""
        return self.filter_by(action=action)

    def find_by_user_and_action(self, user_id: int, action: str) -> List[History]:
        """Get all history records for a user with specific action"""
        return self.filter_by(user_id=user_id, action=action)

    def find_recent_transactions(self, limit: int = 10) -> List[History]:
        """Get most recent transactions"""
        stmt = (
            select(History)
            .order_by(History.created_at.desc())
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

    def find_transactions_in_date_range(self, start_date, end_date) -> List[History]:
        """Get transactions within a date range"""
        stmt = (
            select(History)
            .where(History.created_at >= start_date)
            .where(History.created_at <= end_date)
            .order_by(History.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def get_user_transaction_summary(self, user_id: int) -> dict:
        """Get summary of user's transaction history"""
        buy_transactions = self.filter_by(user_id=user_id, action="buy")
        sell_transactions = self.filter_by(user_id=user_id, action="sell")
        
        total_bought = sum(t.quantity for t in buy_transactions)
        total_sold = sum(t.quantity for t in sell_transactions)
        total_spent = sum(t.price * t.quantity for t in buy_transactions)
        total_earned = sum(t.price * t.quantity for t in sell_transactions)
        
        return {
            "total_bought": total_bought,
            "total_sold": total_sold,
            "total_spent": total_spent,
            "total_earned": total_earned,
            "net_quantity": total_bought - total_sold,
            "net_amount": total_earned - total_spent
        }
