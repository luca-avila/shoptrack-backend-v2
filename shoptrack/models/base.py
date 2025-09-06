from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from ..database import Base


class TimestampMixin:
    """Mixin to add timestamp fields to models"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """Base model class that other models inherit from"""
    __abstract__ = True
    
    def to_dict(self, exclude=None):
        """Convert model instance to dictionary, excluding sensitive fields"""
        exclude = exclude or []
        # Default sensitive fields to exclude
        sensitive_fields = ['password', 'secret', 'token', 'key']
        exclude = exclude + sensitive_fields
        
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }
    
    def __repr__(self):
        """String representation of the model"""
        class_name = self.__class__.__name__
        return f"<{class_name}(id={getattr(self, 'id', None)})>"
