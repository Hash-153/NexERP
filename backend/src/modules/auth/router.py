"""
NexERP Auth & RBAC REST API Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserCreate,
    UserResponse,
    RoleCreate,
    RoleResponse,
    PermissionResponse,
    TenantCreate,
    TenantResponse
)
from backend.src.modules.auth.services import AuthService, RBACService, TenantService

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticate user with email and password, returning JWT access & refresh tokens."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await AuthService.authenticate(db, req, ip_address=client_ip, user_agent=user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Exchange a valid refresh token for a fresh access & refresh token pair."""
    return await AuthService.refresh_tokens(db, req.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch profile, roles, and permissions of the currently authenticated user."""
    user = await AuthService.get_user_by_id(db, current_user.id)
    roles, permissions = AuthService.extract_roles_and_permissions(user)
    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
        roles=roles,
        permissions=permissions,
        created_at=user.created_at
    )


# User Management
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: CurrentUser = Depends(RequirePermission("auth:users:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new user account under the current tenant organization."""
    user = await RBACService.create_user(db, current_user.tenant_id, payload)
    roles, permissions = AuthService.extract_roles_and_permissions(user)
    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
        roles=roles,
        permissions=permissions,
        created_at=user.created_at
    )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(RequirePermission("auth:users:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all users under the current tenant organization."""
    users = await RBACService.list_users(db, current_user.tenant_id, skip=skip, limit=limit)
    response = []
    for u in users:
        roles, perms = AuthService.extract_roles_and_permissions(u)
        response.append(UserResponse(
            id=u.id,
            tenant_id=u.tenant_id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            phone_number=u.phone_number,
            is_superuser=u.is_superuser,
            is_active=u.is_active,
            roles=roles,
            permissions=perms,
            created_at=u.created_at
        ))
    return response


# Roles & Permissions
@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: CurrentUser = Depends(RequirePermission("auth:roles:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all configured roles with their granted permissions."""
    return await RBACService.list_roles(db, current_user.tenant_id)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreate,
    current_user: CurrentUser = Depends(RequirePermission("auth:roles:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new role with specific permission assignments."""
    return await RBACService.create_role(db, current_user.tenant_id, payload)


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: CurrentUser = Depends(RequirePermission("auth:roles:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all available system permissions."""
    return await RBACService.list_all_permissions(db)


# Tenant Management
@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    current_user: CurrentUser = Depends(RequirePermission("admin:all")),
    db: AsyncSession = Depends(get_db_session)
):
    """Provision a new tenant organization (SuperAdmin only)."""
    return await TenantService.provision_tenant(db, payload)


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    current_user: CurrentUser = Depends(RequirePermission("admin:all")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all tenant organizations in the system."""
    return await TenantService.list_tenants(db)
