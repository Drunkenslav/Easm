"""
Asset management service
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from loguru import logger

from app.models import Asset, Vulnerability
from app.models.enums import AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate, AssetWithStats


class AssetService:
    """Service for managing assets"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_asset(
        self,
        asset_create: AssetCreate,
        tenant_id: Optional[str] = None,
        discovery_method: str = "manual",
    ) -> Asset:
        """
        Create a new asset

        Args:
            asset_create: Asset creation data
            tenant_id: Tenant ID (for multi-tenancy)
            discovery_method: How the asset was discovered

        Returns:
            Created Asset object
        """
        now = datetime.utcnow().isoformat()

        asset = Asset(
            type=asset_create.type.value,
            value=asset_create.value,
            name=asset_create.name,
            status=asset_create.status.value,
            criticality=asset_create.criticality,
            tags=asset_create.tags,
            notes=asset_create.notes,
            scan_enabled=asset_create.scan_enabled,
            tenant_id=tenant_id,
            discovered_at=now,
            last_seen_at=now,
            discovery_method=discovery_method,
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)

        logger.info(f"Created asset {asset.type}:{asset.value}")

        return asset

    async def get_asset(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID"""
        return await self.db.get(Asset, asset_id)

    async def get_assets(
        self,
        tenant_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[AssetStatus] = None,
        asset_type: Optional[str] = None,
    ) -> List[Asset]:
        """
        Get list of assets with filters

        Args:
            tenant_id: Filter by tenant
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by status
            asset_type: Filter by type

        Returns:
            List of Asset objects
        """
        stmt = select(Asset)

        # Apply filters
        filters = []
        if tenant_id:
            filters.append(Asset.tenant_id == tenant_id)
        if status:
            filters.append(Asset.status == status.value)
        if asset_type:
            filters.append(Asset.type == asset_type)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.offset(skip).limit(limit).order_by(Asset.created_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_asset_with_stats(self, asset_id: int) -> Optional[AssetWithStats]:
        """
        Get asset with vulnerability statistics

        Args:
            asset_id: Asset ID

        Returns:
            AssetWithStats or None
        """
        asset = await self.get_asset(asset_id)
        if not asset:
            return None

        # Count vulnerabilities
        stmt = select(func.count(Vulnerability.id)).where(
            Vulnerability.asset_id == asset_id
        )
        result = await self.db.execute(stmt)
        vuln_count = result.scalar() or 0

        # Count by severity
        stmt = select(
            Vulnerability.severity,
            func.count(Vulnerability.id)
        ).where(
            Vulnerability.asset_id == asset_id
        ).group_by(Vulnerability.severity)

        result = await self.db.execute(stmt)
        severity_counts = {row[0]: row[1] for row in result}

        # Get last vulnerability
        stmt = select(Vulnerability.created_at).where(
            Vulnerability.asset_id == asset_id
        ).order_by(Vulnerability.created_at.desc()).limit(1)

        result = await self.db.execute(stmt)
        last_vuln = result.scalar_one_or_none()

        # Convert to AssetWithStats
        asset_dict = {
            **asset.__dict__,
            "vulnerability_count": vuln_count,
            "vulnerability_count_by_severity": severity_counts,
            "last_vulnerability_found_at": last_vuln,
        }

        return AssetWithStats(**asset_dict)

    async def update_asset(
        self,
        asset_id: int,
        asset_update: AssetUpdate,
    ) -> Asset:
        """
        Update an asset

        Args:
            asset_id: Asset ID
            asset_update: Asset update data

        Returns:
            Updated Asset object
        """
        asset = await self.db.get(Asset, asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Update fields
        update_data = asset_update.model_dump(exclude_unset=True)

        # Handle enum fields
        if "type" in update_data:
            update_data["type"] = update_data["type"].value
        if "status" in update_data:
            update_data["status"] = update_data["status"].value

        for field, value in update_data.items():
            setattr(asset, field, value)

        # Update last_seen_at
        asset.last_seen_at = datetime.utcnow().isoformat()

        await self.db.commit()
        await self.db.refresh(asset)

        logger.info(f"Updated asset {asset.id}")

        return asset

    async def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset

        Args:
            asset_id: Asset ID

        Returns:
            True if deleted, False if not found
        """
        asset = await self.db.get(Asset, asset_id)
        if not asset:
            return False

        await self.db.delete(asset)
        await self.db.commit()

        logger.info(f"Deleted asset {asset.id}")

        return True

    async def count_assets(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[AssetStatus] = None,
    ) -> int:
        """
        Count assets with filters

        Args:
            tenant_id: Filter by tenant
            status: Filter by status

        Returns:
            Asset count
        """
        stmt = select(func.count(Asset.id))

        filters = []
        if tenant_id:
            filters.append(Asset.tenant_id == tenant_id)
        if status:
            filters.append(Asset.status == status.value)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self.db.execute(stmt)
        return result.scalar() or 0


def get_asset_service(db: AsyncSession) -> AssetService:
    """Get asset service instance"""
    return AssetService(db)
