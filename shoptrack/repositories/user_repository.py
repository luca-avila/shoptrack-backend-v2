from .base import BaseRepository
from ..models.user import User
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)
    
    def find_by_username(self, username: str) -> Optional[User]:
        return self.get_by(username=username)
    
    def find_by_email(self, email: str) -> Optional[User]:
        return self.get_by(email=email)

    def get_with_products(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.products))
        return self.session.execute(stmt).scalar_one_or_none()