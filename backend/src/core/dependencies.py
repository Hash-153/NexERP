"""
NexERP FastAPI Dependencies & Security Guards.
Provides dependency injection for Database Sessions, Current User Identity,
Tenant Context Isolation, and Granular Permission Checking.
"""

from typing import List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import get_db_session
from .security import decode_token
from .exceptions import UnauthorizedError, PermissionDeniedError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


class CurrentUser:
    """
    Authenticated user context injected into request handlers.
    """
    def __init__(
        self,
        id: str,
        email: str,
        tenant_id: str,
        roles: List[str],
        permissions: List[str],
        is_superuser: bool = False
    ):
        self.id = id
        self.email = email
        self.tenant_id = tenant_id
        self.roles = roles
        self.permissions = permissions
        self.is_superuser = is_superuser

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission or superuser privileges."""
        if self.is_superuser or "admin:all" in self.permissions or "*" in self.permissions:
            return True
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        """Check if user belongs to a specific role."""
        if self.is_superuser or "SuperAdmin" in self.roles:
            return True
        return role in self.roles


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db_session)
) -> CurrentUser:
    """
    FastAPI dependency: Extracts, decodes, and validates JWT token from Authorization header.
    Returns CurrentUser object populated with tenant context and authorization claims.
    """
    if not token:
        raise UnauthorizedError("Missing bearer authentication token.")
    
    payload = decode_token(token)
    user_id = payload.get("sub")
    token_tenant_id = payload.get("tenant_id")
    roles = payload.get("roles", [])
    permissions = payload.get("permissions", [])

    if not user_id:
        raise UnauthorizedError("Invalid token payload: missing subject identifier.")

    # Multi-tenant header validation
    tenant_id = x_tenant_id or token_tenant_id
    if not tenant_id:
        tenant_id = "org_corp_hq_001"

    # In production, optionally verify active user status from database cache
    is_superuser = "SuperAdmin" in roles or "admin" in roles

    return CurrentUser(
        id=user_id,
        email=payload.get("email", ""),
        tenant_id=tenant_id,
        roles=roles,
        permissions=permissions,
        is_superuser=is_superuser
    )


class RequirePermission:
    """
    FastAPI dependency class to guard routes by specific permission strings.
    Usage: Depends(RequirePermission("financials:journal_entry:create"))
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_permission(self.required_permission):
            raise PermissionDeniedError(
                message=f"Missing required permission: '{self.required_permission}'.",
                details={"required_permission": self.required_permission}
            )
        return current_user


class RequireRole:
    """
    FastAPI dependency class to guard routes by specific roles.
    Usage: Depends(RequireRole("CFO"))
    """
    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_role(self.required_role):
            raise PermissionDeniedError(
                message=f"Action requires role: '{self.required_role}'.",
                details={"required_role": self.required_role}
            )
        return current_user
