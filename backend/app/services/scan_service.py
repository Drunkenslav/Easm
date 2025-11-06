"""
Scan service for managing vulnerability scans
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models import Scan, ScanTemplate, Asset, Vulnerability
from app.models.enums import ScanStatus, VulnerabilityState
from app.schemas.scan import ScanCreate, ScanTemplateCreate
from app.services.nuclei import (
    get_nuclei_scanner,
    NucleiScanConfig,
    NucleiScanResult,
)
from app.services.nuclei.converter import nuclei_result_to_vulnerability_data


class ScanService:
    """Service for managing vulnerability scans"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._nuclei_scanner = None  # Lazy-load to avoid requiring Nuclei for read operations

    @property
    def nuclei_scanner(self):
        """Lazy-load Nuclei scanner only when needed"""
        if self._nuclei_scanner is None:
            self._nuclei_scanner = get_nuclei_scanner()
        return self._nuclei_scanner

    async def create_scan(
        self,
        scan_create: ScanCreate,
        user_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> Scan:
        """
        Create a new scan

        Args:
            scan_create: Scan creation data
            user_id: User creating the scan
            tenant_id: Tenant ID (for multi-tenancy)

        Returns:
            Created Scan object
        """
        # Verify asset exists
        asset = await self.db.get(Asset, scan_create.asset_id)
        if not asset:
            raise ValueError(f"Asset {scan_create.asset_id} not found")

        # Get template if provided
        template = None
        if scan_create.template_id:
            template = await self.db.get(ScanTemplate, scan_create.template_id)
            if not template:
                raise ValueError(f"Template {scan_create.template_id} not found")

        # Create scan
        scan = Scan(
            name=scan_create.name or f"Scan of {asset.value}",
            asset_id=scan_create.asset_id,
            target=scan_create.target,
            template_id=scan_create.template_id,
            config=scan_create.config,
            status=ScanStatus.PENDING.value,
            created_by_user_id=user_id,
            tenant_id=tenant_id,
        )

        self.db.add(scan)
        await self.db.commit()
        await self.db.refresh(scan)

        logger.info(f"Created scan {scan.id} for asset {asset.value}")

        return scan

    async def execute_scan(self, scan_id: int) -> Scan:
        """
        Execute a scan using Nuclei

        Args:
            scan_id: Scan ID to execute

        Returns:
            Updated Scan object with results
        """
        # Get scan
        scan = await self.db.get(Scan, scan_id)
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        # Get asset
        asset = await self.db.get(Asset, scan.asset_id)
        if not asset:
            raise ValueError(f"Asset {scan.asset_id} not found")

        # Update status to running
        scan.status = ScanStatus.RUNNING.value
        scan.started_at = datetime.utcnow().isoformat()
        await self.db.commit()

        logger.info(f"Starting scan {scan.id} for target {scan.target}")

        try:
            # Build Nuclei configuration
            nuclei_config = await self._build_nuclei_config(scan)

            # Execute scan
            result: NucleiScanResult = await self.nuclei_scanner.scan(nuclei_config)

            # Update scan with results
            scan.status = ScanStatus.COMPLETED.value if result.success else ScanStatus.FAILED.value
            scan.completed_at = datetime.utcnow().isoformat()
            scan.duration_seconds = int(result.duration_seconds)
            scan.vulnerabilities_found = result.total_vulnerabilities
            scan.vulnerabilities_by_severity = result.vulnerabilities_by_severity
            scan.nuclei_output = result.stdout

            if not result.success:
                scan.error_message = result.error_message

            await self.db.commit()

            # Create vulnerability records
            if result.success and result.vulnerabilities:
                await self._create_vulnerabilities(scan, asset, result)

            # Update asset last scanned time
            asset.last_scanned_at = datetime.utcnow().isoformat()
            await self.db.commit()

            logger.info(
                f"Scan {scan.id} completed. "
                f"Found {result.total_vulnerabilities} vulnerabilities"
            )

            return scan

        except Exception as e:
            logger.error(f"Scan {scan.id} failed: {str(e)}")

            # Update scan status to failed
            scan.status = ScanStatus.FAILED.value
            scan.completed_at = datetime.utcnow().isoformat()
            scan.error_message = str(e)
            await self.db.commit()

            raise

    async def _build_nuclei_config(self, scan: Scan) -> NucleiScanConfig:
        """
        Build Nuclei configuration from scan and template

        Args:
            scan: Scan object

        Returns:
            NucleiScanConfig
        """
        config = scan.config or {}

        # Get template if exists
        template = None
        if scan.template_id:
            template = await self.db.get(ScanTemplate, scan.template_id)

        # Build config with template defaults and scan overrides
        nuclei_config = NucleiScanConfig(
            targets=[scan.target],
            templates=config.get("templates") or (template.nuclei_templates if template else None),
            tags=config.get("tags") or (template.nuclei_tags if template else None),
            exclude_tags=config.get("exclude_tags") or (template.nuclei_exclude_tags if template else None),
            severity=config.get("severity") or (template.nuclei_severity if template else None),
            rate_limit=config.get("rate_limit") or (template.rate_limit if template else 150),
            bulk_size=config.get("bulk_size") or (template.bulk_size if template else 25),
            threads=config.get("threads") or (template.threads if template else 25),
            timeout=config.get("timeout") or (template.timeout if template else 3600),
        )

        return nuclei_config

    async def _create_vulnerabilities(
        self,
        scan: Scan,
        asset: Asset,
        result: NucleiScanResult,
    ) -> List[Vulnerability]:
        """
        Create vulnerability records from Nuclei results

        Args:
            scan: Scan object
            asset: Asset object
            result: Nuclei scan result

        Returns:
            List of created Vulnerability objects
        """
        created_vulnerabilities = []

        for nuclei_result in result.vulnerabilities:
            # Convert Nuclei result to vulnerability data
            vuln_data = nuclei_result_to_vulnerability_data(
                nuclei_result,
                asset.id,
                scan.id,
            )

            # Add tenant ID if present
            if scan.tenant_id:
                vuln_data["tenant_id"] = scan.tenant_id

            # Check for existing vulnerability with same hash (deduplication)
            existing_vuln = await self._find_existing_vulnerability(
                vuln_data["hash"],
                asset.id,
            )

            if existing_vuln:
                # Update occurrence count and last seen
                existing_vuln.occurrences += 1
                existing_vuln.last_seen_at = datetime.utcnow().isoformat()
                logger.info(
                    f"Vulnerability {existing_vuln.id} seen again "
                    f"(occurrence {existing_vuln.occurrences})"
                )
            else:
                # Create new vulnerability
                vulnerability = Vulnerability(**vuln_data)
                vulnerability.state = VulnerabilityState.NEW.value
                self.db.add(vulnerability)
                created_vulnerabilities.append(vulnerability)

        await self.db.commit()

        logger.info(
            f"Created {len(created_vulnerabilities)} new vulnerabilities for scan {scan.id}"
        )

        return created_vulnerabilities

    async def _find_existing_vulnerability(
        self,
        vuln_hash: str,
        asset_id: int,
    ) -> Optional[Vulnerability]:
        """
        Find existing vulnerability by hash

        Args:
            vuln_hash: Vulnerability hash
            asset_id: Asset ID

        Returns:
            Vulnerability if found, None otherwise
        """
        stmt = select(Vulnerability).where(
            Vulnerability.hash == vuln_hash,
            Vulnerability.asset_id == asset_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def cancel_scan(self, scan_id: int) -> Scan:
        """
        Cancel a running scan

        Args:
            scan_id: Scan ID

        Returns:
            Updated Scan object
        """
        scan = await self.db.get(Scan, scan_id)
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        if scan.status not in [ScanStatus.PENDING.value, ScanStatus.QUEUED.value, ScanStatus.RUNNING.value]:
            raise ValueError(f"Cannot cancel scan in status {scan.status}")

        scan.status = ScanStatus.CANCELLED.value
        scan.completed_at = datetime.utcnow().isoformat()

        await self.db.commit()
        await self.db.refresh(scan)

        logger.info(f"Cancelled scan {scan.id}")

        return scan

    async def create_template(
        self,
        template_create: ScanTemplateCreate,
        tenant_id: Optional[str] = None,
    ) -> ScanTemplate:
        """
        Create a scan template

        Args:
            template_create: Template creation data
            tenant_id: Tenant ID (for multi-tenancy)

        Returns:
            Created ScanTemplate object
        """
        template = ScanTemplate(
            **template_create.model_dump(),
            tenant_id=tenant_id,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        logger.info(f"Created scan template {template.id}: {template.name}")

        return template

    async def get_scan(self, scan_id: int) -> Optional[Scan]:
        """Get scan by ID"""
        return await self.db.get(Scan, scan_id)

    async def get_template(self, template_id: int) -> Optional[ScanTemplate]:
        """Get template by ID"""
        return await self.db.get(ScanTemplate, template_id)


def get_scan_service(db: AsyncSession) -> ScanService:
    """Get scan service instance"""
    return ScanService(db)
