"""
NexERP Cryptographic Audit Trail & SOX Section 404 Logging Engine.
Constructs immutable, tamper-evident audit logs using SHA-256 hash chains.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.modules.governance.models import AuditLog
from backend.src.modules.governance.enums import AuditActionType


class AuditTrailService:
    """
    Cryptographic SOX Audit Trail Service.
    """

    @classmethod
    def compute_sha256_hash(cls, payload: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
        """
        Compute deterministic SHA-256 digest of audit block including previous block hash.
        """
        serialized = json.dumps(payload, sort_keys=True, default=str)
        chain_data = f"{previous_hash or 'GENESIS_BLOCK_NEXERP_000000000000'}::{serialized}"
        return hashlib.sha256(chain_data.encode("utf-8")).hexdigest()

    @classmethod
    async def log_mutation(
        cls,
        db: AsyncSession,
        tenant_id: str,
        entity_name: str,
        entity_id: str,
        action_type: str,
        user_id: str,
        user_email: Optional[str] = None,
        changed_fields: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Record a tamper-evident audit event chained to the latest audit entry hash for the tenant.
        """
        # Fetch latest entry hash
        latest_query = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(1)
        )
        res = await db.execute(latest_query)
        latest_log = res.scalar_one_or_none()
        prev_hash = latest_log.entry_hash if latest_log else None

        block_payload = {
            "tenant_id": tenant_id,
            "entity_name": entity_name,
            "entity_id": entity_id,
            "action_type": action_type,
            "user_id": user_id,
            "changed_fields": changed_fields,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        entry_hash = cls.compute_sha256_hash(block_payload, prev_hash)

        log = AuditLog(
            tenant_id=tenant_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action_type=action_type,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            changed_fields=changed_fields,
            previous_hash=prev_hash,
            entry_hash=entry_hash
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @classmethod
    async def list_audit_trail(
        cls,
        db: AsyncSession,
        tenant_id: str,
        entity_name: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
        if entity_name:
            query = query.where(AuditLog.entity_name == entity_name)
        if entity_id:
            query = query.where(AuditLog.entity_id == entity_id)
        query = query.order_by(AuditLog.created_at.desc()).limit(limit)

        res = await db.execute(query)
        return list(res.scalars().all())
