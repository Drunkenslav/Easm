"""
Security utilities for authentication and authorization
Simple token-based auth without JWT/cryptography dependencies
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib
import json
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# In-memory token store (in production, use Redis or database)
_token_store = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a simple access token without JWT"""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)

    # Calculate expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    # Store token data with expiration
    _token_store[token] = {
        "data": data.copy(),
        "exp": expire.timestamp()
    }

    return token


def decode_access_token(token: str) -> dict:
    """Decode and verify a token"""
    # Check if token exists
    if token not in _token_store:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = _token_store[token]

    # Check if token is expired
    if datetime.utcnow().timestamp() > token_data["exp"]:
        # Remove expired token
        del _token_store[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data["data"]


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current authenticated user
    This is a placeholder - will be implemented when we create the User model
    """
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # TODO: Fetch user from database
    return {"user_id": user_id}


def check_tier_access(required_tier: str):
    """
    Decorator to check if current tier has access to a feature
    required_tier: minimum tier required (A, B, or C)
    """
    tier_levels = {"A": 1, "B": 2, "C": 3}

    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_tier_level = tier_levels.get(settings.app_tier, 0)
            required_tier_level = tier_levels.get(required_tier, 0)

            if current_tier_level < required_tier_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This feature requires Tier {required_tier} or higher"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
