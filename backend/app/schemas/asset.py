"""
Pydantic schemas for Asset model
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_serializer, field_validator
from app.models.enums import AssetType, AssetStatus
from app.schemas.base import TimestampSchema


class AssetBase(BaseModel):
    """Base asset schema"""
    type: AssetType
    value: str = Field(..., max_length=500)
    name: Optional[str] = Field(None, max_length=255)
    status: AssetStatus = AssetStatus.ACTIVE
    criticality: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    tags: List[str] = []
    notes: Optional[str] = None
    scan_enabled: bool = True


class AssetCreate(AssetBase):
    """Schema for creating a new asset"""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an asset"""
    type: Optional[AssetType] = None
    value: Optional[str] = Field(None, max_length=500)
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[AssetStatus] = None
    criticality: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    scan_enabled: Optional[bool] = None
    ip_address: Optional[str] = None
    ports: Optional[List[int]] = None
    services: Optional[Dict[str, Any]] = None
    technologies: Optional[List[str]] = None


class AssetInDB(AssetBase, TimestampSchema):
    """Schema for asset in database"""
    id: int
    tenant_id: Optional[str] = None
    ip_address: Optional[str] = None
    ports: List[int] = []
    services: Dict[str, Any] = {}
    technologies: List[str] = []
    dns_records: Dict[str, Any] = {}
    discovered_at: Optional[str] = None
    last_seen_at: Optional[str] = None
    discovery_method: Optional[str] = None
    last_scanned_at: Optional[str] = None
    custom_metadata: Dict[str, Any] = {}


class Asset(AssetInDB):
    """Public asset schema"""
    pass


class AssetWithStats(Asset):
    """Asset schema with vulnerability statistics"""
    vulnerability_count: int = 0
    vulnerability_count_by_severity: Dict[str, int] = {}
    last_vulnerability_found_at: Optional[str] = None

    @field_validator('last_vulnerability_found_at', mode='before')
    @classmethod
    def validate_last_vuln_time(cls, v: Union[str, datetime, None]) -> Optional[str]:
        """Convert datetime to ISO format string before validation"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v
