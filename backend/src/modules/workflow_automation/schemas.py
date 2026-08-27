"""Notification and automation API contracts."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: str
    notification_type: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=2)
    severity: str = Field(default="INFO", pattern="^(INFO|SUCCESS|WARNING|ERROR|CRITICAL)$")
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    deduplication_key: Optional[str] = None


class NotificationResponse(NotificationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime


class NotificationReadRequest(BaseModel):
    is_read: bool = True


class AutomationRuleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    event_type: str = Field(min_length=2, max_length=80)
    condition: Dict[str, Any] = Field(default_factory=dict)
    action_type: str = Field(pattern="^(NOTIFY_USER|NOTIFY_ROLE|CREATE_TASK|WEBHOOK)$")
    action_config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AutomationRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    name: str
    event_type: str
    action_type: str
    enabled: bool
    execution_count: int
    last_executed_at: Optional[datetime]
    created_at: datetime


class AutomationEvent(BaseModel):
    event_id: str = Field(min_length=2, max_length=120)
    event_type: str = Field(min_length=2, max_length=80)
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class AutomationExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    rule_id: str
    event_id: str
    event_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    result_json: Optional[str]
