from .base import BaseModel
from sqlalchemy import String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Session(BaseModel):
    __tablename__ = "session"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires={self.expires})>"