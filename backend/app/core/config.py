"""
Configuration management for the EASM platform.
Supports three tiers: A (Open Source), B (On-Prem), C (Cloud SaaS)
"""
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Application settings with tier-based feature flags"""

    # Application
    app_name: str = Field(default="EASM Platform", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(env="SECRET_KEY")

    # Tier Configuration
    app_tier: Literal["A", "B", "C"] = Field(default="A", env="APP_TIER")

    # Database
    database_url: str = Field(env="DATABASE_URL")

    # Redis (Tier B/C only)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")

    # Celery (Tier B/C only)
    celery_broker_url: Optional[str] = Field(default=None, env="CELERY_BROKER_URL")
    celery_result_backend: Optional[str] = Field(default=None, env="CELERY_RESULT_BACKEND")

    # JWT Authentication
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Nuclei Configuration
    nuclei_path: str = Field(default="/usr/local/bin/nuclei", env="NUCLEI_PATH")
    nuclei_templates_path: str = Field(default="./nuclei-templates", env="NUCLEI_TEMPLATES_PATH")
    nuclei_rate_limit: int = Field(default=150, env="NUCLEI_RATE_LIMIT")
    nuclei_bulk_size: int = Field(default=25, env="NUCLEI_BULK_SIZE")
    nuclei_threads: int = Field(default=25, env="NUCLEI_THREADS")

    # Scanning Configuration
    max_concurrent_scans: int = Field(default=5, env="MAX_CONCURRENT_SCANS")
    scan_timeout: int = Field(default=3600, env="SCAN_TIMEOUT")

    # Multi-tenancy (Tier C only)
    multi_tenant: bool = Field(default=False, env="MULTI_TENANT")
    default_tenant: str = Field(default="default", env="DEFAULT_TENANT")

    # Email (optional)
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    email_from: Optional[str] = Field(default=None, env="EMAIL_FROM")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    # Feature flags based on tier
    @property
    def has_scheduled_scans(self) -> bool:
        """Scheduled scans available in Tier B and C"""
        return self.app_tier in ["B", "C"]

    @property
    def has_multi_user(self) -> bool:
        """Multi-user support in Tier B and C"""
        return self.app_tier in ["B", "C"]

    @property
    def has_rbac(self) -> bool:
        """RBAC available in Tier B and C"""
        return self.app_tier in ["B", "C"]

    @property
    def has_asset_discovery(self) -> bool:
        """Advanced asset discovery in Tier C"""
        return self.app_tier == "C"

    @property
    def has_distributed_scanning(self) -> bool:
        """Distributed scanning in Tier C"""
        return self.app_tier == "C"

    @property
    def has_api_rate_limiting(self) -> bool:
        """API rate limiting in Tier C"""
        return self.app_tier == "C"

    @property
    def has_sso(self) -> bool:
        """SSO/SAML in Tier C"""
        return self.app_tier == "C"

    @property
    def has_audit_logs(self) -> bool:
        """Audit logging in Tier C"""
        return self.app_tier == "C"

    @property
    def uses_sqlite(self) -> bool:
        """Check if using SQLite (Tier A default)"""
        return self.database_url.startswith("sqlite")

    @property
    def uses_postgresql(self) -> bool:
        """Check if using PostgreSQL (Tier B/C)"""
        return "postgresql" in self.database_url


# Global settings instance
settings = Settings()
