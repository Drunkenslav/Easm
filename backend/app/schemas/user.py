"""
Pydantic schemas for User model
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import UserRole
from app.schemas.base import TimestampSchema


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase, TimestampSchema):
    """Schema for user in database (with all fields)"""
    id: int
    is_superuser: bool
    tenant_id: Optional[str] = None
    last_login_at: Optional[str] = None


class User(UserInDB):
    """Public user schema (without sensitive data)"""
    pass


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    tenant_id: Optional[str] = None
