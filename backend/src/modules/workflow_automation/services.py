"""Tenant-safe notification inbox and deterministic automation engine."""

import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.core.exceptions import EntityNotFoundError
from .models import AutomationExecution, AutomationRule, Notification, NotificationDelivery
from .schemas import AutomationEvent, AutomationRuleCreate, NotificationCreate


class NotificationService:
    """Owns durable in-app notifications and delivery attempt bookkeeping."""

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    async def create(cls, db: AsyncSession, tenant_id: str, payload: NotificationCreate) -> Notification:
        if payload.deduplication_key:
            result = await db.execute(select(Notification).where(Notification.tenant_id == tenant_id, Notification.user_id == payload.user_id, Notification.deduplication_key == payload.deduplication_key, Notification.is_deleted == False))
            existing = result.scalar_one_or_none()
            if existing:
                return existing
        notification = Notification(tenant_id=tenant_id, is_read=False, **payload.model_dump())
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @classmethod
    async def list_for_user(cls, db: AsyncSession, tenant_id: str, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        query = select(Notification).where(Notification.tenant_id == tenant_id, Notification.user_id == user_id, Notification.is_deleted == False).order_by(Notification.created_at.desc()).limit(min(max(limit, 1), 200))
        if unread_only:
            query = query.where(Notification.is_read == False)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def mark_read(cls, db: AsyncSession, tenant_id: str, user_id: str, notification_id: str, is_read: bool = True) -> Notification:
        result = await db.execute(select(Notification).where(Notification.id == notification_id, Notification.tenant_id == tenant_id, Notification.user_id == user_id, Notification.is_deleted == False))
        notification = result.scalar_one_or_none()
        if not notification:
            raise EntityNotFoundError("Notification not found")
        notification.is_read = is_read
        notification.read_at = cls.now() if is_read else None
        await db.commit()
        await db.refresh(notification)
        return notification

    @classmethod
    async def unread_count(cls, db: AsyncSession, tenant_id: str, user_id: str) -> int:
        result = await db.execute(select(Notification.id).where(Notification.tenant_id == tenant_id, Notification.user_id == user_id, Notification.is_read == False, Notification.is_deleted == False))
        return len(result.all())

    @classmethod
    async def queue_delivery(cls, db: AsyncSession, tenant_id: str, notification_id: str, channel: str, destination: str) -> NotificationDelivery:
        result = await db.execute(select(Notification).where(Notification.id == notification_id, Notification.tenant_id == tenant_id, Notification.is_deleted == False))
        if not result.scalar_one_or_none():
            raise EntityNotFoundError("Notification not found")
        delivery = NotificationDelivery(tenant_id=tenant_id, notification_id=notification_id, channel=channel, destination=destination, status="PENDING", attempt_count=0)
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        return delivery


class WorkflowAutomationService:
    """Evaluates simple JSON conditions and records exactly-once event executions."""

    @classmethod
    async def create_rule(cls, db: AsyncSession, tenant_id: str, payload: AutomationRuleCreate) -> AutomationRule:
        rule = AutomationRule(tenant_id=tenant_id, condition_json=json.dumps(payload.condition, sort_keys=True), action_config_json=json.dumps(payload.action_config, sort_keys=True), **payload.model_dump(exclude={"condition", "action_config"}))
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    def matches(condition: dict, payload: dict) -> bool:
        for key, expected in condition.items():
            actual = payload.get(key)
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True

    @classmethod
    async def process_event(cls, db: AsyncSession, tenant_id: str, event: AutomationEvent) -> List[AutomationExecution]:
        result = await db.execute(select(AutomationRule).where(AutomationRule.tenant_id == tenant_id, AutomationRule.event_type == event.event_type, AutomationRule.enabled == True, AutomationRule.is_deleted == False))
        executions = []
        for rule in result.scalars().all():
            existing_result = await db.execute(select(AutomationExecution).where(AutomationExecution.tenant_id == tenant_id, AutomationExecution.rule_id == rule.id, AutomationExecution.event_id == event.event_id))
            if existing_result.scalar_one_or_none() or not cls.matches(json.loads(rule.condition_json), event.payload):
                continue
            now = datetime.now(timezone.utc)
            execution = AutomationExecution(tenant_id=tenant_id, rule_id=rule.id, event_id=event.event_id, event_type=event.event_type, status="COMPLETED", started_at=now, completed_at=now, result_json=json.dumps({"action_type": rule.action_type, "entity_id": event.entity_id}))
            rule.execution_count += 1
            rule.last_executed_at = now
            db.add(execution)
            executions.append(execution)
            config = json.loads(rule.action_config_json)
            if rule.action_type == "NOTIFY_USER" and config.get("user_id"):
                await NotificationService.create(db, tenant_id, NotificationCreate(user_id=config["user_id"], notification_type="AUTOMATION", title=config.get("title", rule.name), message=config.get("message", f"Automation triggered by {event.event_type}"), entity_type=event.entity_type, entity_id=event.entity_id, deduplication_key=f"{rule.id}:{event.event_id}"))
        if executions:
            await db.commit()
            for execution in executions:
                await db.refresh(execution)
        return executions

    @classmethod
    async def list_rules(cls, db: AsyncSession, tenant_id: str) -> List[AutomationRule]:
        result = await db.execute(select(AutomationRule).where(AutomationRule.tenant_id == tenant_id, AutomationRule.is_deleted == False).order_by(AutomationRule.name.asc()))
        return list(result.scalars().all())
