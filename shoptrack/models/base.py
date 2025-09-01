from datetime import datetime
from shoptrack.database import db

class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
