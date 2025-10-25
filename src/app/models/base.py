from ..core.database import Base as DatabaseBase
from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func

class BaseModel(DatabaseBase):
    __abstract__ = True
    __table_args__ = {"schema": "wannabeaiops"}
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self, allowed_fields=None):
        """
        Convert model instance to dictionary
        """
        if allowed_fields is None:
            allowed_fields = [column.name for column in self.__table__.columns]

        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name in allowed_fields
        }
    
    def __repr__(self):
        """
        String representation of the model
        """
        return f"<{self.__class__.__name__}(id={self.id})>"


__all__ = ["BaseModel"]