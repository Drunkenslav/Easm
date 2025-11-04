"""
API dependencies
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.models.enums import UserRole
from app.services.auth_service import get_auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current authenticated user from token
    Returns None if no token or invalid token (for Tier A single-user mode)
    """
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except Exception:
        return None

    # Get user from database
    auth_service = get_auth_service(db)
    user = await auth_service.get_user(int(user_id))

    if user is None or not user.is_active:
        return None

    return user


async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """
    Require an authenticated user
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Require an admin user
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required.",
        )
    return current_user


async def get_current_manager_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Require a manager or admin user
    """
    if not current_user.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Manager role or higher required.",
        )
    return current_user


async def get_current_user_with_edit_permission(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Require a user with edit permissions (analyst or higher)
    """
    if not current_user.can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Edit permission required.",
        )
    return current_user


def get_tenant_id(current_user: Optional[User] = Depends(get_current_user)) -> Optional[str]:
    """
    Get tenant ID from current user
    Returns None if no user or Tier A/B
    """
    if not current_user:
        return None
    return current_user.tenant_id
