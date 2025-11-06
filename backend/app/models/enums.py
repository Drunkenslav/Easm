"""
Enumerations for database models
"""
import enum


class UserRole(str, enum.Enum):
    """User roles for RBAC (Tier B/C)"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class ScanStatus(str, enum.Enum):
    """Scan execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VulnerabilityState(str, enum.Enum):
    """Vulnerability workflow states"""
    NEW = "new"
    TRIAGING = "triaging"
    INVESTIGATING = "investigating"
    REMEDIATION = "remediation"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"


class VulnerabilitySeverity(str, enum.Enum):
    """Vulnerability severity levels (from Nuclei)"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetType(str, enum.Enum):
    """Asset types"""
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP = "ip"
    URL = "url"
    API_ENDPOINT = "api_endpoint"


class AssetStatus(str, enum.Enum):
    """Asset discovery status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
