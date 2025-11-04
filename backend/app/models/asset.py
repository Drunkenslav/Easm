"""
Asset model for EASM inventory
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin
from app.models.enums import AssetType, AssetStatus


class Asset(Base, TimestampMixin, TenantMixin):
    """
    Asset model representing discoverable attack surface elements
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)

    # Asset identification
    type = Column(String(50), nullable=False, index=True)  # AssetType enum
    value = Column(String(500), nullable=False, index=True)  # domain, IP, URL, etc.
    name = Column(String(255))  # Friendly name

    # Status
    status = Column(String(50), default=AssetStatus.ACTIVE.value, nullable=False, index=True)

    # Discovery metadata
    discovered_at = Column(String(50))  # ISO date when first discovered
    last_seen_at = Column(String(50))  # ISO date when last seen
    discovery_method = Column(String(100))  # How it was discovered (manual, subdomain_enum, etc.)

    # Technical details
    ip_address = Column(String(45))  # IPv4 or IPv6
    ports = Column(JSON, default=[])  # List of open ports
    services = Column(JSON, default={})  # Detected services
    technologies = Column(JSON, default=[])  # Detected technologies (Wappalyzer style)
    dns_records = Column(JSON, default={})  # DNS records if applicable

    # Ownership and classification
    tags = Column(JSON, default=[])  # User-defined tags
    criticality = Column(String(50), default="medium")  # low, medium, high, critical
    notes = Column(Text)

    # Scanning
    last_scanned_at = Column(String(50))  # ISO date of last scan
    scan_enabled = Column(Boolean, default=True)  # Whether to include in scans

    # Relationships
    vulnerabilities = relationship("Vulnerability", back_populates="asset", cascade="all, delete-orphan")
    scans = relationship("Scan", back_populates="asset", cascade="all, delete-orphan")

    # Metadata
    metadata = Column(JSON, default={})  # Additional flexible data

    def __repr__(self):
        return f"<Asset {self.type}:{self.value}>"
