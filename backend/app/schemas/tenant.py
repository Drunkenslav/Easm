"""
Pydantic schemas for Tenant model (Tier C)
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class TenantBase(BaseModel):
    """Base tenant schema"""
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=100, pattern="^[a-z0-9-]+$")
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class TenantCreate(TenantBase):
    """Schema for creating a tenant"""
    max_assets: int = Field(default=1000, ge=1, le=100000)
    max_scans_per_day: int = Field(default=100, ge=1, le=10000)
    max_concurrent_scans: int = Field(default=5, ge=1, le=50)
    plan: str = Field(default="standard", pattern="^(standard|premium|enterprise)$")


class TenantUpdate(BaseModel):
    """Schema for updating a tenant"""
    name: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    max_assets: Optional[int] = Field(None, ge=1, le=100000)
    max_scans_per_day: Optional[int] = Field(None, ge=1, le=10000)
    max_concurrent_scans: Optional[int] = Field(None, ge=1, le=50)
    plan: Optional[str] = Field(None, pattern="^(standard|premium|enterprise)$")
    settings: Optional[Dict[str, Any]] = None


class TenantInDB(TenantBase):
    """Schema for tenant in database"""
    id: int
    max_assets: int
    max_scans_per_day: int
    max_concurrent_scans: int
    settings: Dict[str, Any] = {}
    plan: str
    subscription_expires_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class Tenant(TenantInDB):
    """Public tenant schema"""
    pass


class TenantWithStats(Tenant):
    """Tenant schema with usage statistics"""
    asset_count: int = 0
    user_count: int = 0
    scan_count_today: int = 0
    vulnerability_count: int = 0
