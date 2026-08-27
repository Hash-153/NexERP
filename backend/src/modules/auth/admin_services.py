"""Security administration services with one-time secret issuance."""

import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError
from .admin_models import APIKey, LoginAudit, TenantFeatureFlag


class SecurityAdministrationService:
    """Manages revocable machine credentials and tenant feature configuration."""

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @classmethod
    async def issue_api_key(cls, db: AsyncSession, tenant_id: str, name: str, scopes: List[str], user_id: str, expires_at: Optional[datetime] = None) -> tuple[str, APIKey]:
        if not name.strip() or not scopes:
            raise ValueError("API key requires a name and at least one scope")
        raw = f"nx_{secrets.token_urlsafe(36)}"
        key = APIKey(tenant_id=tenant_id, name=name.strip(), key_hash=cls._hash(raw), key_prefix=raw[:12], scopes=json.dumps(sorted(set(scopes))), expires_at=expires_at, created_by_id=user_id)
        db.add(key)
        await db.commit()
        await db.refresh(key)
        return raw, key

    @classmethod
    async def authenticate_api_key(cls, db: AsyncSession, tenant_id: str, raw_key: str) -> APIKey:
        result = await db.execute(select(APIKey).where(APIKey.tenant_id == tenant_id, APIKey.key_hash == cls._hash(raw_key), APIKey.revoked_at.is_(None), APIKey.is_deleted == False))
        key = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if not key or (key.expires_at and (key.expires_at.replace(tzinfo=timezone.utc) if key.expires_at.tzinfo is None else key.expires_at) <= now):
            raise ValueError("API key is invalid, expired, or revoked")
        key.last_used_at = now
        await db.commit()
        return key

    @classmethod
    async def revoke_api_key(cls, db: AsyncSession, tenant_id: str, key_id: str) -> APIKey:
        result = await db.execute(select(APIKey).where(APIKey.id == key_id, APIKey.tenant_id == tenant_id, APIKey.is_deleted == False))
        key = result.scalar_one_or_none()
        if not key:
            raise EntityNotFoundError("API key not found")
        key.revoked_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(key)
        return key

    @classmethod
    async def record_login(cls, db: AsyncSession, tenant_id: str, event_type: str, email: Optional[str] = None, user_id: Optional[str] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None, failure_reason: Optional[str] = None) -> LoginAudit:
        if event_type not in {"SUCCESS", "FAILURE", "LOGOUT", "LOCKED"}:
            raise ValueError("Unsupported login audit event")
        audit = LoginAudit(tenant_id=tenant_id, event_type=event_type, email=email, user_id=user_id, ip_address=ip_address, user_agent=user_agent, failure_reason=failure_reason, occurred_at=datetime.now(timezone.utc))
        db.add(audit)
        await db.commit()
        await db.refresh(audit)
        return audit

    @classmethod
    async def set_feature_flag(cls, db: AsyncSession, tenant_id: str, feature_code: str, enabled: bool, user_id: str, description: Optional[str] = None) -> TenantFeatureFlag:
        result = await db.execute(select(TenantFeatureFlag).where(TenantFeatureFlag.tenant_id == tenant_id, TenantFeatureFlag.feature_code == feature_code))
        flag = result.scalar_one_or_none()
        if not flag:
            flag = TenantFeatureFlag(tenant_id=tenant_id, feature_code=feature_code, enabled=enabled, updated_by_id=user_id, description=description)
            db.add(flag)
        else:
            flag.enabled = enabled
            flag.updated_by_id = user_id
            if description is not None:
                flag.description = description
        await db.commit()
        await db.refresh(flag)
        return flag

    @classmethod
    async def enabled(cls, db: AsyncSession, tenant_id: str, feature_code: str) -> bool:
        result = await db.execute(select(TenantFeatureFlag.enabled).where(TenantFeatureFlag.tenant_id == tenant_id, TenantFeatureFlag.feature_code == feature_code, TenantFeatureFlag.is_deleted == False))
        return bool(result.scalar_one_or_none())
