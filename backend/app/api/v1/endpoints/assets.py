"""
Asset management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.asset import Asset, AssetCreate, AssetUpdate, AssetWithStats
from app.models.enums import AssetStatus, AssetType
from app.services.asset_service import get_asset_service
from app.api.deps import (
    get_current_user,
    get_current_user_with_edit_permission,
    get_tenant_id,
)

router = APIRouter()


@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_create: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Create a new asset

    Requires edit permission (analyst role or higher in Tier B/C)
    """
    asset_service = get_asset_service(db)

    asset = await asset_service.create_asset(
        asset_create,
        tenant_id=tenant_id,
        discovery_method="manual"
    )

    return asset


@router.get("/", response_model=List[Asset])
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AssetStatus] = None,
    asset_type: Optional[AssetType] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    List assets with pagination and filters

    Available to all authenticated users in Tier B/C, no auth required in Tier A
    """
    asset_service = get_asset_service(db)

    assets = await asset_service.get_assets(
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        status=status,
        asset_type=asset_type.value if asset_type else None,
    )

    return assets


@router.get("/count")
async def count_assets(
    status: Optional[AssetStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Count assets with filters
    """
    asset_service = get_asset_service(db)

    count = await asset_service.count_assets(
        tenant_id=tenant_id,
        status=status,
    )

    return {"count": count}


@router.get("/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get asset by ID
    """
    asset_service = get_asset_service(db)

    asset = await asset_service.get_asset(asset_id)

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found"
        )

    return asset


@router.get("/{asset_id}/stats", response_model=AssetWithStats)
async def get_asset_with_stats(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get asset with vulnerability statistics
    """
    asset_service = get_asset_service(db)

    asset = await asset_service.get_asset_with_stats(asset_id)

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found"
        )

    return asset


@router.patch("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Update an asset

    Requires edit permission
    """
    asset_service = get_asset_service(db)

    try:
        asset = await asset_service.update_asset(asset_id, asset_update)
        return asset
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Delete an asset

    Requires edit permission. This will also delete all associated scans and vulnerabilities.
    """
    asset_service = get_asset_service(db)

    deleted = await asset_service.delete_asset(asset_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found"
        )
