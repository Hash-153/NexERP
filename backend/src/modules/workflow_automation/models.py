"""Persistent notification inbox and event automation records."""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text
from backend.src.core.database import Base


class Notification(Base):
    __tablename__ = "wa_notifications"
    __table_args__ = (Index("ix_wa_notification_user_unread", "tenant_id", "user_id", "is_read"),)
    user_id = Column(String(36), nullable=False)
    notification_type = Column(String(40), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="INFO")
    entity_type = Column(String(80), nullable=True)
    entity_id = Column(String(36), nullable=True)
    action_url = Column(String(500), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    deduplication_key = Column(String(255), nullable=True, index=True)


class AutomationRule(Base):
    __tablename__ = "wa_automation_rules"
    name = Column(String(150), nullable=False)
    event_type = Column(String(80), nullable=False, index=True)
    condition_json = Column(Text, nullable=False, default="{}")
    action_type = Column(String(40), nullable=False)
    action_config_json = Column(Text, nullable=False, default="{}")
    enabled = Column(Boolean, nullable=False, default=True)
    execution_count = Column(Integer, nullable=False, default=0)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)


class AutomationExecution(Base):
    __tablename__ = "wa_automation_executions"
    __table_args__ = (Index("ix_wa_execution_rule_event", "tenant_id", "rule_id", "event_id"),)
    rule_id = Column(String(36), nullable=False)
    event_id = Column(String(120), nullable=False)
    event_type = Column(String(80), nullable=False)
    status = Column(String(20), nullable=False, default="STARTED")
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)


class NotificationDelivery(Base):
    __tablename__ = "wa_notification_deliveries"
    notification_id = Column(String(36), nullable=False)
    channel = Column(String(20), nullable=False)
    destination = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    attempt_count = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)
