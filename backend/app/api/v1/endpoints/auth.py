"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.schemas.user import Token, User, UserCreate
from app.services.auth_service import get_auth_service
from app.api.deps import get_current_user, get_current_active_user
from app.models import User as UserModel

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 compatible login endpoint

    Returns JWT access token on successful authentication
    """
    auth_service = get_auth_service(db)

    user = await auth_service.authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = auth_service.create_token_for_user(user)

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user

    Note: In Tier A, only one user (admin) exists by default.
    In Tier B/C, this allows user registration (may require admin approval).
    """
    if not settings.has_multi_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User registration not available in Tier A. Multi-user support requires Tier B or C.",
        )

    auth_service = get_auth_service(db)

    try:
        user = await auth_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    Get current authenticated user information
    """
    return current_user


@router.get("/init")
async def initialize_default_user(
    db: AsyncSession = Depends(get_db),
):
    """
    Initialize default admin user for Tier A

    This is called on first setup to create the default admin user.
    """
    auth_service = get_auth_service(db)
    user = await auth_service.ensure_default_user()

    return {
        "message": "Default user initialized",
        "username": user.username,
        "note": "Please change the default password"
    }
