"""
Initialize database with admin user and mock data
Run this automatically on container startup
"""
# Load .env FIRST before importing any app modules
from dotenv import load_dotenv
import os
load_dotenv()

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
from app.models import User, Asset, Vulnerability, Scan, ScanTemplate
from app.models.user import UserRole
from app.models.asset import AssetType
from app.models.vulnerability import VulnerabilitySeverity, VulnerabilityState
from app.models.scan import ScanStatus

# Get DATABASE_URL and convert to async format
_database_url = os.getenv("DATABASE_URL", "sqlite:///./data/easm.db")
if _database_url.startswith("sqlite://"):
    DATABASE_URL = _database_url.replace("sqlite://", "sqlite+aiosqlite://")
elif "postgresql" in _database_url and "asyncpg" not in _database_url:
    DATABASE_URL = _database_url.replace("postgresql://", "postgresql+asyncpg://")
else:
    DATABASE_URL = _database_url

async def init_database():
    """Initialize database with admin user and mock data"""
    print("🔧 Initializing database...")

    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create all tables first
    print("📊 Creating database tables...")
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin user already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            print("👤 Creating admin user...")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                role=UserRole.ADMIN.value,
                is_active=True,
                is_superuser=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            print(f"✅ Admin user created: username=admin, password=admin123")
        else:
            print(f"✅ Admin user already exists: {admin_user.username}")

        # Check if mock data already exists
        result = await session.execute(select(Asset))
        existing_assets = result.scalars().all()

        if len(existing_assets) > 0:
            print(f"✅ Mock data already exists ({len(existing_assets)} assets)")
            return

        print("📊 Creating mock data...")

        # Create scan templates
        now = datetime.utcnow()
        templates = [
            ScanTemplate(
                name="Quick Scan",
                description="Fast vulnerability scan with critical/high severity only",
                nuclei_severity=["critical", "high"],
                nuclei_tags=["cve"],
                created_at=now,
                updated_at=now
            ),
            ScanTemplate(
                name="Full Scan",
                description="Comprehensive vulnerability scan with all severities",
                nuclei_severity=["critical", "high", "medium", "low"],
                nuclei_tags=[],
                created_at=now,
                updated_at=now
            )
        ]
        for template in templates:
            session.add(template)
        await session.commit()
        print(f"✅ Created {len(templates)} scan templates")

        # Create assets
        assets_data = [
            {"type": AssetType.DOMAIN, "value": "example.com", "name": "Main Website", "criticality": "high"},
            {"type": AssetType.DOMAIN, "value": "api.example.com", "name": "API Server", "criticality": "critical"},
            {"type": AssetType.DOMAIN, "value": "staging.example.com", "name": "Staging Environment", "criticality": "medium"},
            {"type": AssetType.IP, "value": "192.168.1.100", "name": "Internal Server", "criticality": "high"},
            {"type": AssetType.IP, "value": "10.0.0.50", "name": "Database Server", "criticality": "critical"},
            {"type": AssetType.URL, "value": "https://example.com/admin", "name": "Admin Panel", "criticality": "critical"},
            {"type": AssetType.DOMAIN, "value": "dev.example.com", "name": "Development Server", "criticality": "low"},
        ]

        assets = []
        for i, asset_data in enumerate(assets_data):
            asset = Asset(
                type=asset_data["type"].value,
                value=asset_data["value"],
                name=asset_data["name"],
                notes=f"Mock asset for testing",
                criticality=asset_data["criticality"],
                tags=["mock", "test"],
                custom_metadata={},
                status="active",
                scan_enabled=True,
                discovered_at=now.isoformat(),
                created_at=now,
                updated_at=now
            )
            session.add(asset)
            assets.append(asset)

        await session.commit()

        # Refresh to get IDs
        for asset in assets:
            await session.refresh(asset)

        print(f"✅ Created {len(assets)} mock assets")

        # Create scans
        scans_data = [
            {"asset_idx": 0, "status": ScanStatus.COMPLETED, "vulns": 5},
            {"asset_idx": 1, "status": ScanStatus.COMPLETED, "vulns": 8},
            {"asset_idx": 2, "status": ScanStatus.RUNNING, "vulns": 0},
            {"asset_idx": 3, "status": ScanStatus.COMPLETED, "vulns": 3},
            {"asset_idx": 4, "status": ScanStatus.FAILED, "vulns": 0},
            {"asset_idx": 5, "status": ScanStatus.COMPLETED, "vulns": 12},
            {"asset_idx": 6, "status": ScanStatus.PENDING, "vulns": 0},
        ]

        scans = []
        for scan_data in scans_data:
            asset = assets[scan_data["asset_idx"]]
            scan = Scan(
                name=f"Scan of {asset.name}",
                asset_id=asset.id,
                target=asset.value,
                status=scan_data["status"].value,
                config={},
                started_at=now.isoformat() if scan_data["status"] != ScanStatus.PENDING else None,
                completed_at=(now + timedelta(minutes=5)).isoformat() if scan_data["status"] == ScanStatus.COMPLETED else None,
                duration_seconds=300 if scan_data["status"] == ScanStatus.COMPLETED else None,
                vulnerabilities_found=scan_data["vulns"],
                vulnerabilities_by_severity={"critical": scan_data["vulns"] // 3, "high": scan_data["vulns"] // 2} if scan_data["vulns"] > 0 else {},
                error_message="Network timeout" if scan_data["status"] == ScanStatus.FAILED else None,
                created_at=now,
                updated_at=now
            )
            session.add(scan)
            scans.append(scan)

        await session.commit()
        print(f"✅ Created {len(scans)} mock scans")

        # Create vulnerabilities
        vulnerabilities_data = [
            {"asset_idx": 0, "severity": VulnerabilitySeverity.CRITICAL, "state": VulnerabilityState.NEW, "title": "SQL Injection in Login Form"},
            {"asset_idx": 0, "severity": VulnerabilitySeverity.HIGH, "state": VulnerabilityState.TRIAGING, "title": "Cross-Site Scripting (XSS)"},
            {"asset_idx": 1, "severity": VulnerabilitySeverity.CRITICAL, "state": VulnerabilityState.REMEDIATION, "title": "Authentication Bypass"},
            {"asset_idx": 1, "severity": VulnerabilitySeverity.HIGH, "state": VulnerabilityState.NEW, "title": "Insecure Direct Object Reference"},
            {"asset_idx": 1, "severity": VulnerabilitySeverity.MEDIUM, "state": VulnerabilityState.INVESTIGATING, "title": "Missing Security Headers"},
            {"asset_idx": 3, "severity": VulnerabilitySeverity.CRITICAL, "state": VulnerabilityState.NEW, "title": "Remote Code Execution"},
            {"asset_idx": 3, "severity": VulnerabilitySeverity.HIGH, "state": VulnerabilityState.REMEDIATION, "title": "Path Traversal Vulnerability"},
            {"asset_idx": 5, "severity": VulnerabilitySeverity.CRITICAL, "state": VulnerabilityState.NEW, "title": "Privilege Escalation"},
            {"asset_idx": 5, "severity": VulnerabilitySeverity.HIGH, "state": VulnerabilityState.NEW, "title": "Server-Side Request Forgery"},
            {"asset_idx": 5, "severity": VulnerabilitySeverity.HIGH, "state": VulnerabilityState.TRIAGING, "title": "XML External Entity (XXE)"},
            {"asset_idx": 5, "severity": VulnerabilitySeverity.MEDIUM, "state": VulnerabilityState.RESOLVED, "title": "Weak Password Policy"},
            {"asset_idx": 5, "severity": VulnerabilitySeverity.MEDIUM, "state": VulnerabilityState.FALSE_POSITIVE, "title": "Outdated Software Version"},
            {"asset_idx": 0, "severity": VulnerabilitySeverity.LOW, "state": VulnerabilityState.ACCEPTED_RISK, "title": "Information Disclosure"},
            {"asset_idx": 1, "severity": VulnerabilitySeverity.HIGH, "state": VulnerabilityState.NEW, "title": "Broken Access Control"},
            {"asset_idx": 5, "severity": VulnerabilitySeverity.CRITICAL, "state": VulnerabilityState.REMEDIATION, "title": "Insecure Deserialization"},
        ]

        for idx, vuln_data in enumerate(vulnerabilities_data):
            asset_idx = vuln_data["asset_idx"]
            # Find a completed scan for this asset
            scan_for_asset = next((s for s in scans if s.asset_id == assets[asset_idx].id and s.status == "completed"), None)
            if not scan_for_asset:
                continue  # Skip if no completed scan

            vulnerability = Vulnerability(
                asset_id=assets[asset_idx].id,
                scan_id=scan_for_asset.id,
                template_id=f"mock-template-{idx}",
                template_name=f"mock/{vuln_data['title'].lower().replace(' ', '-')}",
                name=vuln_data["title"],
                description=f"Mock vulnerability: {vuln_data['title']}",
                severity=vuln_data["severity"].value,
                state=vuln_data["state"].value,
                matched_at=f"https://{assets[asset_idx].value}/vulnerable",
                cvss_score=str(9.8 if vuln_data["severity"] == VulnerabilitySeverity.CRITICAL else 7.5),
                cve_ids=[f"CVE-2024-{1000 + idx}"],
                cwe_ids=[f"CWE-{79 + idx}"],
                tags=["mock", "test"],
                reference_urls=["https://nvd.nist.gov/vuln/detail/CVE-2024-1000"],
                created_at=now,
                updated_at=now
            )
            session.add(vulnerability)

        await session.commit()
        print(f"✅ Created {len(vulnerabilities_data)} mock vulnerabilities")

        print("✅ Database initialization complete!")
        print("")
        print("🔐 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("")
        print("📊 Mock data created:")
        print(f"   - {len(assets)} assets")
        print(f"   - {len(scans)} scans")
        print(f"   - {len(vulnerabilities_data)} vulnerabilities")
        print("")

if __name__ == "__main__":
    try:
        asyncio.run(init_database())
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
