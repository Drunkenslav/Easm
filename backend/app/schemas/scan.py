"""
Pydantic schemas for Scan and ScanTemplate models
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.enums import ScanStatus


class ScanTemplateBase(BaseModel):
    """Base scan template schema"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    nuclei_templates: List[str] = []
    nuclei_severity: List[str] = []
    nuclei_tags: List[str] = []
    nuclei_exclude_tags: List[str] = []
    rate_limit: int = Field(default=150, ge=1, le=1000)
    bulk_size: int = Field(default=25, ge=1, le=100)
    threads: int = Field(default=25, ge=1, le=100)
    timeout: int = Field(default=3600, ge=60, le=7200)
    options: Dict[str, Any] = {}


class ScanTemplateCreate(ScanTemplateBase):
    """Schema for creating a scan template"""
    pass


class ScanTemplateUpdate(BaseModel):
    """Schema for updating a scan template"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    nuclei_templates: Optional[List[str]] = None
    nuclei_severity: Optional[List[str]] = None
    nuclei_tags: Optional[List[str]] = None
    nuclei_exclude_tags: Optional[List[str]] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=1000)
    bulk_size: Optional[int] = Field(None, ge=1, le=100)
    threads: Optional[int] = Field(None, ge=1, le=100)
    timeout: Optional[int] = Field(None, ge=60, le=7200)
    options: Optional[Dict[str, Any]] = None


class ScanTemplateInDB(ScanTemplateBase):
    """Schema for scan template in database"""
    id: int
    tenant_id: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ScanTemplate(ScanTemplateInDB):
    """Public scan template schema"""
    pass


class ScanBase(BaseModel):
    """Base scan schema"""
    name: Optional[str] = Field(None, max_length=255)
    target: str = Field(..., max_length=500)
    template_id: Optional[int] = None
    config: Dict[str, Any] = {}


class ScanCreate(ScanBase):
    """Schema for creating a scan"""
    asset_id: int


class ScanUpdate(BaseModel):
    """Schema for updating a scan"""
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[ScanStatus] = None


class ScanInDB(ScanBase):
    """Schema for scan in database"""
    id: int
    asset_id: int
    status: ScanStatus
    tenant_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    vulnerabilities_found: int = 0
    vulnerabilities_by_severity: Dict[str, int] = {}
    error_message: Optional[str] = None
    celery_task_id: Optional[str] = None
    worker_hostname: Optional[str] = None
    created_by_user_id: Optional[int] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class Scan(ScanInDB):
    """Public scan schema"""
    pass


class ScanWithDetails(Scan):
    """Scan schema with additional details"""
    nuclei_output: Optional[str] = None


class ScanTrigger(BaseModel):
    """Schema for triggering a scan"""
    asset_ids: List[int] = Field(..., min_length=1)
    template_id: Optional[int] = None
    config_override: Dict[str, Any] = {}
