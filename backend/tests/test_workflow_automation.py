"""Notification and workflow automation behavior tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.workflow_automation.schemas import AutomationEvent, AutomationRuleCreate, NotificationCreate
from backend.src.modules.workflow_automation.services import NotificationService, WorkflowAutomationService


@pytest.mark.asyncio
async def test_notification_deduplication_and_read_state(db_session: AsyncSession):
    tenant = "org_corp_hq_001"
    payload = NotificationCreate(user_id="usr_admin_001", notification_type="SLA", title="Ticket at risk", message="A service ticket is approaching its SLA.", deduplication_key="ticket-1-at-risk")
    first = await NotificationService.create(db_session, tenant, payload)
    second = await NotificationService.create(db_session, tenant, payload)
    assert first.id == second.id
    assert await NotificationService.unread_count(db_session, tenant, "usr_admin_001") == 1
    await NotificationService.mark_read(db_session, tenant, "usr_admin_001", first.id)
    assert await NotificationService.unread_count(db_session, tenant, "usr_admin_001") == 0


@pytest.mark.asyncio
async def test_automation_event_executes_once_and_notifies_user(db_session: AsyncSession):
    tenant = "org_corp_hq_001"
    rule = await WorkflowAutomationService.create_rule(db_session, tenant, AutomationRuleCreate(name="Escalate urgent tickets", event_type="TICKET_CREATED", condition={"priority": "URGENT"}, action_type="NOTIFY_USER", action_config={"user_id": "usr_admin_001", "title": "Urgent ticket", "message": "Review the new urgent ticket."}))
    event = AutomationEvent(event_id="evt-001", event_type="TICKET_CREATED", entity_type="ServiceTicket", entity_id="ticket-001", payload={"priority": "URGENT"})
    first = await WorkflowAutomationService.process_event(db_session, tenant, event)
    second = await WorkflowAutomationService.process_event(db_session, tenant, event)
    assert len(first) == 1
    assert second == []
    notifications = await NotificationService.list_for_user(db_session, tenant, "usr_admin_001")
    assert len(notifications) == 1
    assert rule.execution_count == 1
