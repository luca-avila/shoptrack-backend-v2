from .base import BaseModel
from typing import Optional, List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(BaseModel):
    __tablename__ = 'user'
    
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120), unique=True)

    products: Mapped[List['Product']] = relationship(
        back_populates='owner',
        cascade='all, delete-orphan'
    )
    history: Mapped[List['History']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )
    sessions: Mapped[List['Session']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"