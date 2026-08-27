"""
NexERP RBAC & User Management Service.
Handles roles, permissions, user assignments, and authorization matrix synchronization.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.security import hash_password
from backend.src.core.exceptions import EntityNotFoundError, EntityAlreadyExistsError, BusinessRuleViolationError
from backend.src.modules.auth.models import User, Role, Permission, UserRole, RolePermission
from backend.src.modules.auth.schemas import UserCreate, UserUpdate, RoleCreate
from backend.src.modules.auth.enums import SYSTEM_PERMISSIONS


class RBACService:
    """
    Role-Based Access Control and User provisioning manager.
    """

    @classmethod
    async def seed_permissions(cls, db: AsyncSession) -> int:
        """Seed standard enterprise permissions into the database."""
        created_count = 0
        for code, module, desc in SYSTEM_PERMISSIONS:
            query = select(Permission).where(Permission.code == code)
            result = await db.execute(query)
            existing = result.scalar_one_or_none()
            if not existing:
                perm = Permission(code=code, module=module, description=desc)
                db.add(perm)
                created_count += 1
        await db.commit()
        return created_count

    @classmethod
    async def create_user(cls, db: AsyncSession, tenant_id: str, payload: UserCreate) -> User:
        """Create new user account within specified tenant organization."""
        query = select(User).where(User.email == payload.email.lower().strip())
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"User with email '{payload.email}' already exists.")

        user = User(
            tenant_id=tenant_id,
            email=payload.email.lower().strip(),
            hashed_password=hash_password(payload.password),
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            phone_number=payload.phone_number,
            is_superuser=payload.is_superuser,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.flush()

        if payload.role_ids:
            for role_id in payload.role_ids:
                user_role = UserRole(tenant_id=tenant_id, user_id=user.id, role_id=role_id)
                db.add(user_role)

        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def list_users(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """List active users for a tenant."""
        query = (
            select(User)
            .where(User.tenant_id == tenant_id, User.is_deleted == False)
            .options(
                selectinload(User.user_roles)
                .selectinload(UserRole.role)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def create_role(cls, db: AsyncSession, tenant_id: str, payload: RoleCreate) -> Role:
        """Create custom enterprise role with assigned permissions."""
        role = Role(
            tenant_id=tenant_id,
            name=payload.name.strip(),
            description=payload.description,
            is_system_role=False
        )
        db.add(role)
        await db.flush()

        if payload.permission_ids:
            for perm_id in payload.permission_ids:
                rp = RolePermission(tenant_id=tenant_id, role_id=role.id, permission_id=perm_id)
                db.add(rp)

        await db.commit()
        await db.refresh(role)
        return role

    @classmethod
    async def list_roles(cls, db: AsyncSession, tenant_id: str) -> List[Role]:
        """List all active roles with their associated permissions."""
        query = (
            select(Role)
            .where(Role.tenant_id == tenant_id, Role.is_deleted == False)
            .options(
                selectinload(Role.role_permissions)
                .selectinload(RolePermission.permission)
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def list_all_permissions(cls, db: AsyncSession) -> List[Permission]:
        """List all system permissions."""
        query = select(Permission).order_by(Permission.module.asc(), Permission.code.asc())
        result = await db.execute(query)
        return list(result.scalars().all())
