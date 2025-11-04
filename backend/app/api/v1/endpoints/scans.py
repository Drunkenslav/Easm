"""
Scan management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.schemas.scan import (
    Scan,
    ScanCreate,
    ScanUpdate,
    ScanWithDetails,
    ScanTemplate,
    ScanTemplateCreate,
    ScanTemplateUpdate,
    ScanTrigger,
)
from app.models.enums import ScanStatus
from app.services.scan_service import get_scan_service
from app.api.deps import (
    get_current_user,
    get_current_user_with_edit_permission,
    get_tenant_id,
)
from app.models import User

router = APIRouter()


# Scan endpoints

@router.post("/", response_model=Scan, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_create: ScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_edit_permission),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Create a new scan

    Requires edit permission
    """
    scan_service = get_scan_service(db)

    try:
        scan = await scan_service.create_scan(
            scan_create,
            user_id=current_user.id if current_user else None,
            tenant_id=tenant_id,
        )
        return scan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/trigger", response_model=List[Scan], status_code=status.HTTP_201_CREATED)
async def trigger_scans(
    scan_trigger: ScanTrigger,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_edit_permission),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Trigger scans for multiple assets

    Creates scan jobs for each asset and executes them.
    In Tier A, scans run in background tasks.
    In Tier B/C, scans can be queued to Celery.
    """
    from app.services.asset_service import get_asset_service

    scan_service = get_scan_service(db)
    asset_service = get_asset_service(db)

    created_scans = []

    for asset_id in scan_trigger.asset_ids:
        # Verify asset exists
        asset = await asset_service.get_asset(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found"
            )

        # Create scan
        scan_create = ScanCreate(
            asset_id=asset_id,
            target=asset.value,
            template_id=scan_trigger.template_id,
            config=scan_trigger.config_override,
        )

        scan = await scan_service.create_scan(
            scan_create,
            user_id=current_user.id if current_user else None,
            tenant_id=tenant_id,
        )

        created_scans.append(scan)

        # Execute scan in background
        # In Tier B/C, this should use Celery instead
        background_tasks.add_task(scan_service.execute_scan, scan.id)

    return created_scans


@router.get("/", response_model=List[Scan])
async def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[ScanStatus] = Query(None, alias="status"),
    asset_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    List scans with pagination and filters
    """
    from sqlalchemy import select, and_
    from app.models import Scan as ScanModel

    stmt = select(ScanModel)

    # Apply filters
    filters = []
    if tenant_id:
        filters.append(ScanModel.tenant_id == tenant_id)
    if status_filter:
        filters.append(ScanModel.status == status_filter.value)
    if asset_id:
        filters.append(ScanModel.asset_id == asset_id)

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.offset(skip).limit(limit).order_by(ScanModel.created_at.desc())

    result = await db.execute(stmt)
    scans = list(result.scalars().all())

    return scans


@router.get("/{scan_id}", response_model=Scan)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get scan by ID
    """
    scan_service = get_scan_service(db)
    scan = await scan_service.get_scan(scan_id)

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )

    return scan


@router.get("/{scan_id}/details", response_model=ScanWithDetails)
async def get_scan_details(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get scan with full details including Nuclei output
    """
    scan_service = get_scan_service(db)
    scan = await scan_service.get_scan(scan_id)

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )

    return scan


@router.post("/{scan_id}/execute", response_model=Scan)
async def execute_scan(
    scan_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Execute a pending scan

    The scan will run in the background
    """
    scan_service = get_scan_service(db)
    scan = await scan_service.get_scan(scan_id)

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )

    if scan.status != ScanStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scan is not in pending status (current: {scan.status})"
        )

    # Execute in background
    background_tasks.add_task(scan_service.execute_scan, scan_id)

    return scan


@router.post("/{scan_id}/cancel", response_model=Scan)
async def cancel_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Cancel a running or pending scan
    """
    scan_service = get_scan_service(db)

    try:
        scan = await scan_service.cancel_scan(scan_id)
        return scan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Delete a scan

    This will also delete associated vulnerabilities
    """
    from app.models import Scan as ScanModel

    scan = await db.get(ScanModel, scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )

    await db.delete(scan)
    await db.commit()


# Scan template endpoints

@router.post("/templates/", response_model=ScanTemplate, status_code=status.HTTP_201_CREATED)
async def create_scan_template(
    template_create: ScanTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Create a scan template

    Requires edit permission
    """
    scan_service = get_scan_service(db)

    template = await scan_service.create_template(
        template_create,
        tenant_id=tenant_id,
    )

    return template


@router.get("/templates/", response_model=List[ScanTemplate])
async def list_scan_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    List scan templates
    """
    from sqlalchemy import select, and_
    from app.models import ScanTemplate as ScanTemplateModel

    stmt = select(ScanTemplateModel)

    if tenant_id:
        stmt = stmt.where(ScanTemplateModel.tenant_id == tenant_id)

    stmt = stmt.offset(skip).limit(limit).order_by(ScanTemplateModel.created_at.desc())

    result = await db.execute(stmt)
    templates = list(result.scalars().all())

    return templates


@router.get("/templates/{template_id}", response_model=ScanTemplate)
async def get_scan_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get scan template by ID
    """
    scan_service = get_scan_service(db)
    template = await scan_service.get_template(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )

    return template


@router.patch("/templates/{template_id}", response_model=ScanTemplate)
async def update_scan_template(
    template_id: int,
    template_update: ScanTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Update a scan template
    """
    from app.models import ScanTemplate as ScanTemplateModel

    template = await db.get(ScanTemplateModel, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )

    # Update fields
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Delete a scan template
    """
    from app.models import ScanTemplate as ScanTemplateModel

    template = await db.get(ScanTemplateModel, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )

    await db.delete(template)
    await db.commit()
