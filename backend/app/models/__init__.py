# Database models package
from app.core.database import Base

# Import all models here for Alembic to detect them
from app.models.tenant import Tenant
from app.models.user import User
from app.models.asset import Asset
from app.models.scan import Scan, ScanTemplate
from app.models.vulnerability import Vulnerability

# Export all models
__all__ = [
    "Base",
    "Tenant",
    "User",
    "Asset",
    "Scan",
    "ScanTemplate",
    "Vulnerability",
]
