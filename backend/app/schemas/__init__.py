"""
Pydantic schemas package
"""
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserLogin,
    Token,
    TokenData,
)
from app.schemas.asset import (
    Asset,
    AssetCreate,
    AssetUpdate,
    AssetInDB,
    AssetWithStats,
)
from app.schemas.scan import (
    Scan,
    ScanCreate,
    ScanUpdate,
    ScanInDB,
    ScanWithDetails,
    ScanTemplate,
    ScanTemplateCreate,
    ScanTemplateUpdate,
    ScanTemplateInDB,
    ScanTrigger,
)
from app.schemas.vulnerability import (
    Vulnerability,
    VulnerabilityCreate,
    VulnerabilityUpdate,
    VulnerabilityInDB,
    VulnerabilityWithAsset,
    VulnerabilityStateChange,
    VulnerabilityAssignment,
    VulnerabilityStats,
)
from app.schemas.tenant import (
    Tenant,
    TenantCreate,
    TenantUpdate,
    TenantInDB,
    TenantWithStats,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserLogin",
    "Token",
    "TokenData",
    # Asset
    "Asset",
    "AssetCreate",
    "AssetUpdate",
    "AssetInDB",
    "AssetWithStats",
    # Scan
    "Scan",
    "ScanCreate",
    "ScanUpdate",
    "ScanInDB",
    "ScanWithDetails",
    "ScanTemplate",
    "ScanTemplateCreate",
    "ScanTemplateUpdate",
    "ScanTemplateInDB",
    "ScanTrigger",
    # Vulnerability
    "Vulnerability",
    "VulnerabilityCreate",
    "VulnerabilityUpdate",
    "VulnerabilityInDB",
    "VulnerabilityWithAsset",
    "VulnerabilityStateChange",
    "VulnerabilityAssignment",
    "VulnerabilityStats",
    # Tenant
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    "TenantInDB",
    "TenantWithStats",
]
