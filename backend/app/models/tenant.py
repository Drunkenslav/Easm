"""
Tenant model for multi-tenancy (Tier C)
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.core.database import Base
from app.models.base import TimestampMixin


class Tenant(Base, TimestampMixin):
    """
    Tenant model for multi-tenancy support in Tier C
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Contact information
    contact_email = Column(String(255))
    contact_name = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Quotas and limits
    max_assets = Column(Integer, default=1000)
    max_scans_per_day = Column(Integer, default=100)
    max_concurrent_scans = Column(Integer, default=5)

    # Settings (JSON field for flexible configuration)
    settings = Column(JSON, default={})

    # Subscription information
    plan = Column(String(50), default="standard")  # standard, premium, enterprise
    subscription_expires_at = Column(String(50))  # ISO date string

    def __repr__(self):
        return f"<Tenant {self.slug}>"
