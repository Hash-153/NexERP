"""
NexERP Authentication, Tenant, and RBAC Models.
Provides data models for Multi-Tenancy, User Accounts, Granular Permissions, and Active Sessions.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, foreign
from backend.src.core.database import Base


class Tenant(Base):
    """
    Organization boundary entity representing a legal entity or enterprise subsidiary.
    """
    __tablename__ = "auth_tenants"

    name = Column(String(150), nullable=False, doc="Company or Subsidiary legal name")
    code = Column(String(30), nullable=False, unique=True, index=True, doc="Unique tenant identifier code")
    currency = Column(String(3), default="USD", nullable=False, doc="Base operating currency (ISO-4217)")
    tax_identifier = Column(String(50), nullable=True, doc="National Tax Registration Number / EIN / VAT")
    country = Column(String(100), default="United States", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    fiscal_year_start_month = Column(String(20), default="January", nullable=False)

    users = relationship("User", primaryjoin="Tenant.id == foreign(User.tenant_id)", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """
    Enterprise system user account with credentials and role associations.
    """
    __tablename__ = "auth_users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(50), nullable=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", primaryjoin="foreign(User.tenant_id) == Tenant.id", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Role(Base):
    """
    Role entity bundling permission sets (e.g. Accountant, WarehouseManager, ProductionDirector).
    """
    __tablename__ = "auth_roles"

    name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)

    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    """
    Granular permission verb mapped to specific business domain actions.
    """
    __tablename__ = "auth_permissions"

    code = Column(String(100), nullable=False, unique=True, index=True, doc="e.g. financials:journal:post")
    module = Column(String(50), nullable=False, index=True, doc="e.g. Financials, Inventory, HR")
    description = Column(String(255), nullable=True)

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class UserRole(Base):
    """
    Association link mapping users to assigned roles.
    """
    __tablename__ = "auth_user_roles"

    user_id = Column(String(36), ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("auth_roles.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class RolePermission(Base):
    """
    Association link mapping roles to granted permissions.
    """
    __tablename__ = "auth_role_permissions"

    role_id = Column(String(36), ForeignKey("auth_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(String(36), ForeignKey("auth_permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class UserSession(Base):
    """
    Active JWT session record used for token rotation, remote logout, and concurrent session tracking.
    """
    __tablename__ = "auth_user_sessions"

    user_id = Column(String(36), ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash = Column(String(64), nullable=False, index=True)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="sessions")
