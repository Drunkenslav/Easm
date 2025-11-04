"""
Authentication and user management service
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings


class AuthService:
    """Service for authentication and user management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            User if authenticated, None otherwise
        """
        # Find user by username or email
        stmt = select(User).where(
            (User.username == username) | (User.email == username)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        # Update last login
        user.last_login_at = datetime.utcnow().isoformat()
        await self.db.commit()

        logger.info(f"User {user.username} authenticated successfully")

        return user

    async def create_user(
        self,
        user_create: UserCreate,
        tenant_id: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        """
        Create a new user

        Args:
            user_create: User creation data
            tenant_id: Tenant ID (for multi-tenancy)
            is_superuser: Whether user is superuser

        Returns:
            Created User object
        """
        # Check if username exists
        stmt = select(User).where(User.username == user_create.username)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError(f"Username {user_create.username} already exists")

        # Check if email exists
        stmt = select(User).where(User.email == user_create.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError(f"Email {user_create.email} already exists")

        # Create user
        user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password),
            full_name=user_create.full_name,
            role=user_create.role.value,
            is_active=user_create.is_active,
            is_superuser=is_superuser,
            tenant_id=tenant_id,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created user {user.username} with role {user.role}")

        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.db.get(User, user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """
        Update a user

        Args:
            user_id: User ID
            user_update: User update data

        Returns:
            Updated User object
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Update fields
        update_data = user_update.model_dump(exclude_unset=True)

        # Handle password separately
        if "password" in update_data:
            user.hashed_password = get_password_hash(update_data.pop("password"))

        # Update role value
        if "role" in update_data:
            update_data["role"] = update_data["role"].value

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Updated user {user.username}")

        return user

    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = await self.db.get(User, user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()

        logger.info(f"Deleted user {user.username}")

        return True

    def create_token_for_user(self, user: User) -> str:
        """
        Create JWT access token for user

        Args:
            user: User object

        Returns:
            JWT token string
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        }

        if user.tenant_id:
            token_data["tenant_id"] = user.tenant_id

        return create_access_token(token_data)

    async def ensure_default_user(self) -> User:
        """
        Ensure a default admin user exists (for Tier A)

        Returns:
            Default user
        """
        # Check if any user exists
        stmt = select(User)
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        if users:
            return users[0]

        # Create default admin user
        logger.info("Creating default admin user for Tier A")

        default_user = UserCreate(
            email="admin@localhost",
            username="admin",
            password="admin",  # Should be changed in production
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )

        user = await self.create_user(default_user, is_superuser=True)

        logger.warning(
            "Default admin user created with username 'admin' and password 'admin'. "
            "Please change the password immediately!"
        )

        return user


def get_auth_service(db: AsyncSession) -> AuthService:
    """Get auth service instance"""
    return AuthService(db)
