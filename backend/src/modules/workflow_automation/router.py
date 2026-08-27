"""Notification inbox and workflow automation API."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.core.database import get_db_session
from backend.src.core.dependencies import CurrentUser, RequirePermission
from .schemas import AutomationEvent, AutomationExecutionResponse, AutomationRuleCreate, AutomationRuleResponse, NotificationCreate, NotificationReadRequest, NotificationResponse
from .services import NotificationService, WorkflowAutomationService

router = APIRouter(prefix="/workflow-automation", tags=["Workflow Automation"])


@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(unread_only: bool = False, current_user: CurrentUser = Depends(RequirePermission("notifications:read")), db: AsyncSession = Depends(get_db_session)):
    return await NotificationService.list_for_user(db, current_user.tenant_id, current_user.id, unread_only)


@router.get("/notifications/unread-count")
async def unread_count(current_user: CurrentUser = Depends(RequirePermission("notifications:read")), db: AsyncSession = Depends(get_db_session)):
    return {"count": await NotificationService.unread_count(db, current_user.tenant_id, current_user.id)}


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(payload: NotificationCreate, current_user: CurrentUser = Depends(RequirePermission("notifications:manage")), db: AsyncSession = Depends(get_db_session)):
    return await NotificationService.create(db, current_user.tenant_id, payload)


@router.patch("/notifications/{notification_id}", response_model=NotificationResponse)
async def mark_notification(notification_id: str, payload: NotificationReadRequest, current_user: CurrentUser = Depends(RequirePermission("notifications:read")), db: AsyncSession = Depends(get_db_session)):
    return await NotificationService.mark_read(db, current_user.tenant_id, current_user.id, notification_id, payload.is_read)


@router.post("/automation/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(payload: AutomationRuleCreate, current_user: CurrentUser = Depends(RequirePermission("workflow:manage")), db: AsyncSession = Depends(get_db_session)):
    return await WorkflowAutomationService.create_rule(db, current_user.tenant_id, payload)


@router.get("/automation/rules", response_model=List[AutomationRuleResponse])
async def list_automation_rules(current_user: CurrentUser = Depends(RequirePermission("workflow:read")), db: AsyncSession = Depends(get_db_session)):
    return await WorkflowAutomationService.list_rules(db, current_user.tenant_id)


@router.post("/automation/events", response_model=List[AutomationExecutionResponse])
async def process_automation_event(payload: AutomationEvent, current_user: CurrentUser = Depends(RequirePermission("workflow:manage")), db: AsyncSession = Depends(get_db_session)):
    return await WorkflowAutomationService.process_event(db, current_user.tenant_id, payload)
