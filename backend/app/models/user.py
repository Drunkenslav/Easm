"""
User model for authentication and RBAC
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin
from app.models.enums import UserRole


class User(Base, TimestampMixin, TenantMixin):
    """
    User model with role-based access control
    - Tier A: Single user (admin role)
    - Tier B/C: Multi-user with RBAC
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Role (Tier B/C)
    role = Column(String(50), default=UserRole.VIEWER.value, nullable=False)

    # Last login tracking
    last_login_at = Column(String(50))  # ISO date string

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN.value or self.is_superuser

    @property
    def is_manager(self) -> bool:
        """Check if user is manager or higher"""
        return self.role in [UserRole.ADMIN.value, UserRole.MANAGER.value] or self.is_superuser

    @property
    def can_edit(self) -> bool:
        """Check if user can edit resources"""
        return self.role in [UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.ANALYST.value]

    @property
    def can_view(self) -> bool:
        """Check if user can view resources"""
        return self.is_active
