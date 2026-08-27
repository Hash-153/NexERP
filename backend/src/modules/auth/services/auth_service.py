"""
NexERP Authentication & User Session Service.
Handles user authentication, password verification, token issuance, and session revocation.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.config import settings
from backend.src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from backend.src.core.exceptions import (
    UnauthorizedError,
    EntityNotFoundError,
    BusinessRuleViolationError
)
from backend.src.modules.auth.models import User, UserSession, Role, Permission, UserRole, RolePermission
from backend.src.modules.auth.schemas import LoginRequest, TokenResponse, UserResponse, UserCreate


class AuthService:
    """
    Core authentication provider managing user credentials and JWT lifecycle.
    """

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> Optional[User]:
        """Fetch user by email with eagerly loaded roles and permissions."""
        query = (
            select(User)
            .where(User.email == email.lower().strip(), User.is_deleted == False)
            .options(
                selectinload(User.user_roles)
                .selectinload(UserRole.role)
                .selectinload(Role.role_permissions)
                .selectinload(RolePermission.permission)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: str) -> Optional[User]:
        """Fetch user by ID with loaded roles and permissions."""
        query = (
            select(User)
            .where(User.id == user_id, User.is_deleted == False)
            .options(
                selectinload(User.user_roles)
                .selectinload(UserRole.role)
                .selectinload(Role.role_permissions)
                .selectinload(RolePermission.permission)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    def extract_roles_and_permissions(cls, user: User) -> Tuple[list[str], list[str]]:
        """Extract flat lists of role names and permission codes assigned to the user."""
        roles = []
        permissions = set()

        if user.is_superuser:
            permissions.add("admin:all")
            permissions.add("*")

        for ur in user.user_roles:
            if ur.role:
                roles.append(ur.role.name)
                for rp in ur.role.role_permissions:
                    if rp.permission:
                        permissions.add(rp.permission.code)

        return roles, list(permissions)

    @classmethod
    async def authenticate(
        cls,
        db: AsyncSession,
        req: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """
        Validate user credentials, record login timestamp, and generate access/refresh token pair.
        """
        user = await cls.get_user_by_email(db, req.email)
        if not user:
            raise UnauthorizedError("Invalid email or password credentials.")

        if not user.is_active:
            raise UnauthorizedError("User account is deactivated. Contact enterprise administrator.")

        if not verify_password(req.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password credentials.")

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)

        roles, permissions = cls.extract_roles_and_permissions(user)

        # Generate tokens
        access_token = create_access_token(
            subject=user.id,
            tenant_id=user.tenant_id,
            roles=roles,
            permissions=permissions
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            tenant_id=user.tenant_id
        )

        # Hash refresh token for session tracking
        rf_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        session = UserSession(
            tenant_id=user.tenant_id,
            user_id=user.id,
            refresh_token_hash=rf_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        db.add(session)
        await db.commit()

        user_resp = UserResponse(
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

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp
        )

    @classmethod
    async def refresh_tokens(cls, db: AsyncSession, refresh_token: str) -> TokenResponse:
        """
        Validate refresh token, check session active status, and issue fresh access/refresh pair.
        """
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type for refresh operation.")

        user_id = payload.get("sub")
        rf_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()

        query = select(UserSession).where(
            UserSession.refresh_token_hash == rf_hash,
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()

        if not session or session.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedError("Refresh session has expired or was revoked.")

        # Revoke old session (Rotation)
        session.is_revoked = True

        user = await cls.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User is no longer active.")

        roles, permissions = cls.extract_roles_and_permissions(user)

        new_access_token = create_access_token(
            subject=user.id,
            tenant_id=user.tenant_id,
            roles=roles,
            permissions=permissions
        )
        new_refresh_token = create_refresh_token(
            subject=user.id,
            tenant_id=user.tenant_id
        )

        new_rf_hash = hashlib.sha256(new_refresh_token.encode("utf-8")).hexdigest()
        new_session = UserSession(
            tenant_id=user.tenant_id,
            user_id=user.id,
            refresh_token_hash=new_rf_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_session)
        await db.commit()

        user_resp = UserResponse(
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

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp
        )
