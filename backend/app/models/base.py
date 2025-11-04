"""
Base model with common fields
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import declarative_mixin, declared_attr
from app.core.database import Base


@declarative_mixin
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


@declarative_mixin
class TenantMixin:
    """Mixin for multi-tenancy (Tier C only)"""

    @declared_attr
    def tenant_id(cls):
        return Column(String(50), nullable=True, index=True)
