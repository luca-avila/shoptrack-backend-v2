from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
import logging

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model_class: Type[T], session):
        self.model_class = model_class
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, **kwargs) -> T:
        """Create a new record"""
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            return instance
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise

    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by primary key"""
        try:
            stmt = select(self.model_class).where(self.model_class.id == id)
            result = self.session.execute(stmt).scalar_one_or_none()
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching {self.model_class.__name__} id {id}: {e}")
            raise

    def get_all(self) -> List[T]:
        """Get all records"""
        try:
            stmt = select(self.model_class)
            result = self.session.execute(stmt).scalars().all()
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching all {self.model_class.__name__}: {e}")
            raise

    def get_by(self, **filters) -> Optional[T]:
        """Get first record matching filters"""
        try:
            stmt = select(self.model_class)
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model_class, field) == value)
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Error filtering {self.model_class.__name__} by {filters}: {e}")
            raise

    def filter_by(self, **filters) -> List[T]:
        """Get all records matching filters"""
        try:
            stmt = select(self.model_class)
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model_class, field) == value)
            return self.session.execute(stmt).scalars().all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error filtering {self.model_class.__name__} by {filters}: {e}")
            raise

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update record by id"""
        try:
            instance = self.get_by_id(id)
            if instance:
                for field, value in kwargs.items():
                    setattr(instance, field, value)
            return instance
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating {self.model_class.__name__} id {id}: {e}")
            raise

    def delete(self, id: int) -> bool:
        """Delete record by id"""
        try:
            instance = self.get_by_id(id)
            if instance:
                self.session.delete(instance)
                return True
            return False
        except SQLAlchemyError as e:
            self.logger.error(f"Error deleting {self.model_class.__name__} id {id}: {e}")
            raise

    def exists(self, id: int) -> bool:
        return self.get_by_id(id) is not None

    def count(self) -> int:
        try:
            stmt = select(func.count(self.model_class.id))
            return self.session.execute(stmt).scalar()
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting {self.model_class.__name__}: {e}")
            raise