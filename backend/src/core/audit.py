"""
NexERP Core Audit Trail Subsystem.
Provides immutable event capture, state diffing, and forensic change tracking for all enterprise records.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import Base


class AuditLog(Base):
    """
    Immutable audit trail record capturing every state modification in the ERP.
    """
    __tablename__ = "core_audit_logs"

    actor_id = Column(String(36), nullable=True, index=True, doc="User ID who executed the action")
    actor_email = Column(String(255), nullable=True, doc="User email address at time of action")
    action = Column(String(50), nullable=False, index=True, doc="Action verb: CREATE, UPDATE, DELETE, POST, REVERSE, APPROVE, REJECT")
    entity_type = Column(String(100), nullable=False, index=True, doc="Entity name: JournalEntry, PurchaseOrder, etc.")
    entity_id = Column(String(36), nullable=False, index=True, doc="Identifier of modified entity")
    
    previous_state = Column(JSON, nullable=True, doc="Snapshot of entity state before modification")
    new_state = Column(JSON, nullable=True, doc="Snapshot of entity state after modification")
    changes = Column(JSON, nullable=True, doc="Computed delta diff of changed fields")
    
    ip_address = Column(String(45), nullable=True, doc="Client IPv4 or IPv6 address")
    user_agent = Column(String(255), nullable=True, doc="Client browser / API user agent")
    description = Column(Text, nullable=True, doc="Human-readable summary of the operation")


class AuditService:
    """
    Service layer providing audit logging, delta computation, and history retrieval.
    """

    @staticmethod
    def compute_diff(old_dict: Optional[Dict[str, Any]], new_dict: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute field-by-field differences between old and new state dictionaries.
        """
        if not old_dict and not new_dict:
            return {}
        if not old_dict:
            return {k: {"old": None, "new": v} for k, v in new_dict.items() if k not in ("created_at", "updated_at")}
        if not new_dict:
            return {k: {"old": v, "new": None} for k, v in old_dict.items()}

        diff = {}
        all_keys = set(old_dict.keys()).union(set(new_dict.keys()))
        
        ignored_keys = {"created_at", "updated_at", "deleted_at"}
        
        for k in all_keys:
            if k in ignored_keys:
                continue
            old_val = old_dict.get(k)
            new_val = new_dict.get(k)
            if old_val != new_val:
                diff[k] = {"old": old_val, "new": new_val}
                
        return diff

    @classmethod
    async def log_event(
        cls,
        db: AsyncSession,
        tenant_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None
    ) -> AuditLog:
        """
        Create and persist an immutable audit record in the database.
        """
        changes = cls.compute_diff(previous_state, new_state)
        
        audit_entry = AuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_email=actor_email,
            action=action.upper(),
            entity_type=entity_type,
            entity_id=str(entity_id),
            previous_state=previous_state,
            new_state=new_state,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description
        )
        
        db.add(audit_entry)
        await db.flush()
        return audit_entry

    @staticmethod
    async def get_entity_history(
        db: AsyncSession,
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Fetch chronological audit history for a specific business entity.
        """
        query = (
            select(AuditLog)
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
