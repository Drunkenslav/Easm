"""
Scan model for vulnerability scanning jobs
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin
from app.models.enums import ScanStatus


class ScanTemplate(Base, TimestampMixin, TenantMixin):
    """
    Reusable scan configuration templates
    """
    __tablename__ = "scan_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Nuclei configuration
    nuclei_templates = Column(JSON, default=[])  # List of template paths/tags
    nuclei_severity = Column(JSON, default=[])  # Filter by severity
    nuclei_tags = Column(JSON, default=[])  # Template tags to include
    nuclei_exclude_tags = Column(JSON, default=[])  # Template tags to exclude

    # Scan settings
    rate_limit = Column(Integer, default=150)
    bulk_size = Column(Integer, default=25)
    threads = Column(Integer, default=25)
    timeout = Column(Integer, default=3600)

    # Additional options
    options = Column(JSON, default={})  # Additional Nuclei flags

    # Relationships
    scans = relationship("Scan", back_populates="template")

    def __repr__(self):
        return f"<ScanTemplate {self.name}>"


class Scan(Base, TimestampMixin, TenantMixin):
    """
    Scan job model representing individual vulnerability scans
    """
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))

    # Target
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    target = Column(String(500), nullable=False)  # URL/domain/IP to scan

    # Template (optional)
    template_id = Column(Integer, ForeignKey("scan_templates.id", ondelete="SET NULL"), nullable=True)

    # Status
    status = Column(String(50), default=ScanStatus.PENDING.value, nullable=False, index=True)

    # Timing
    started_at = Column(String(50))  # ISO date
    completed_at = Column(String(50))  # ISO date
    duration_seconds = Column(Integer)  # Duration in seconds

    # Configuration (can override template)
    config = Column(JSON, default={})  # Scan configuration

    # Results
    vulnerabilities_found = Column(Integer, default=0)
    vulnerabilities_by_severity = Column(JSON, default={})  # Count by severity

    # Output
    nuclei_output = Column(Text)  # Raw Nuclei output
    error_message = Column(Text)  # Error message if failed

    # Execution metadata
    celery_task_id = Column(String(255))  # Celery task ID (Tier B/C)
    worker_hostname = Column(String(255))  # Worker that ran the scan

    # Created by (for audit)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="scans")
    template = relationship("ScanTemplate", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    created_by = relationship("User")

    def __repr__(self):
        return f"<Scan {self.id}:{self.target}>"
