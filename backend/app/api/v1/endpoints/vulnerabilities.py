"""
Vulnerability management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.vulnerability import (
    Vulnerability,
    VulnerabilityUpdate,
    VulnerabilityStateChange,
    VulnerabilityAssignment,
    VulnerabilityStats,
)
from app.models.enums import VulnerabilityState, VulnerabilitySeverity
from app.services.vulnerability_service import get_vulnerability_service
from app.api.deps import (
    get_current_user,
    get_current_user_with_edit_permission,
    get_tenant_id,
)
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[Vulnerability])
async def list_vulnerabilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    state: Optional[VulnerabilityState] = None,
    severity: Optional[VulnerabilitySeverity] = None,
    asset_id: Optional[int] = None,
    scan_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    List vulnerabilities with pagination and filters

    Available filters:
    - state: Vulnerability state (new, triaging, investigating, etc.)
    - severity: Vulnerability severity (info, low, medium, high, critical)
    - asset_id: Filter by specific asset
    - scan_id: Filter by specific scan
    """
    vuln_service = get_vulnerability_service(db)

    vulnerabilities = await vuln_service.get_vulnerabilities(
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        state=state,
        severity=severity,
        asset_id=asset_id,
        scan_id=scan_id,
    )

    return vulnerabilities


@router.get("/stats", response_model=VulnerabilityStats)
async def get_vulnerability_stats(
    asset_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Get vulnerability statistics

    Provides counts by severity, state, and asset
    """
    vuln_service = get_vulnerability_service(db)

    stats = await vuln_service.get_stats(
        tenant_id=tenant_id,
        asset_id=asset_id,
    )

    return stats


@router.get("/{vuln_id}", response_model=Vulnerability)
async def get_vulnerability(
    vuln_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get vulnerability by ID
    """
    vuln_service = get_vulnerability_service(db)
    vulnerability = await vuln_service.get_vulnerability(vuln_id)

    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vulnerability {vuln_id} not found"
        )

    return vulnerability


@router.patch("/{vuln_id}", response_model=Vulnerability)
async def update_vulnerability(
    vuln_id: int,
    vuln_update: VulnerabilityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Update a vulnerability

    Requires edit permission
    """
    vuln_service = get_vulnerability_service(db)

    try:
        vulnerability = await vuln_service.update_vulnerability(vuln_id, vuln_update)
        return vulnerability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{vuln_id}/state", response_model=Vulnerability)
async def change_vulnerability_state(
    vuln_id: int,
    state_change: VulnerabilityStateChange,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_edit_permission),
):
    """
    Change vulnerability state

    Workflow states:
    - new: Newly discovered
    - triaging: Being evaluated
    - investigating: Under investigation
    - remediation: Being fixed
    - resolved: Fixed and verified
    - false_positive: Not a real vulnerability
    - accepted_risk: Risk accepted, no action needed

    Requires edit permission
    """
    vuln_service = get_vulnerability_service(db)

    try:
        vulnerability = await vuln_service.change_state(
            vuln_id,
            state_change,
            user_id=current_user.id if current_user else None,
        )
        return vulnerability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{vuln_id}/assign", response_model=Vulnerability)
async def assign_vulnerability(
    vuln_id: int,
    assignment: VulnerabilityAssignment,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Assign vulnerability to a user

    Requires edit permission (Tier B/C)
    """
    from app.core.config import settings

    if not settings.has_multi_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assignment not available in Tier A. Multi-user support requires Tier B or C.",
        )

    vuln_service = get_vulnerability_service(db)

    try:
        vulnerability = await vuln_service.assign_vulnerability(
            vuln_id,
            assignment.assigned_to_user_id,
        )
        return vulnerability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{vuln_id}/accept-risk", response_model=Vulnerability)
async def accept_risk(
    vuln_id: int,
    reason: str = Query(..., min_length=10),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_edit_permission),
):
    """
    Accept risk for a vulnerability

    This marks the vulnerability as an accepted risk and moves it to the accepted_risk state.
    Requires a reason (minimum 10 characters).

    Requires edit permission
    """
    vuln_service = get_vulnerability_service(db)

    try:
        vulnerability = await vuln_service.accept_risk(
            vuln_id,
            reason,
            user_id=current_user.id if current_user else None,
        )
        return vulnerability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{vuln_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vulnerability(
    vuln_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_with_edit_permission),
):
    """
    Delete a vulnerability

    Requires edit permission
    """
    vuln_service = get_vulnerability_service(db)

    deleted = await vuln_service.delete_vulnerability(vuln_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vulnerability {vuln_id} not found"
        )
