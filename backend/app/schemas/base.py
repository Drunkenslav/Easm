"""
Base schemas with common functionality
"""
from datetime import datetime
from pydantic import BaseModel, field_serializer


class TimestampSchema(BaseModel):
    """Base schema with timestamp serialization"""
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at', check_fields=False)
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Convert datetime to ISO format string"""
        if dt:
            return dt.isoformat()
        return None

    class Config:
        from_attributes = True
