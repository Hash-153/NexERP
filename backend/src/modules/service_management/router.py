"""REST API for service desk and field service workflows."""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.core.database import get_db_session
from backend.src.core.dependencies import CurrentUser, RequirePermission
from .models import ServiceActivity
from .schemas import ActivityCreate, AssetCreate, AssetResponse, ContractCreate, ContractResponse, TicketCreate, TicketResponse, TicketStatusUpdate, TicketSummary
from .services import ServiceManagementService
from .field_models import DispatchOrder
from .field_schemas import (ArticleCreate, ArticleResponse, DispatchCreate, DispatchResponse, DispatchStatusUpdate,
                            FeedbackCreate, FeedbackResponse, MaintenancePlanCreate, MaintenancePlanResponse,
                            TechnicianCreate, TechnicianResponse)
from .field_services import CustomerExperienceService, FieldService, KnowledgeService, PreventiveMaintenanceService
from .billing_schemas import (ChargeCreate, ChargeResponse, ChargeStatusUpdate, EscalationAcknowledge,
                               EscalationResponse, InvoiceBatchCreate, InvoiceBatchResponse)
from .billing_services import SLAEscalationService, ServiceBillingService
from .portal_schemas import (AppointmentRequestCreate, AppointmentResponse, AppointmentReview,
                              ConversationCreate, ConversationResponse, PortalTokenResponse)
from .portal_services import CustomerPortalService

router = APIRouter(prefix="/service-management", tags=["Service Management"])


def viewer():
    return RequirePermission("service:read")


def manager():
    return RequirePermission("service:manage")


@router.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(payload: ContractCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.create_contract(db, current_user.tenant_id, payload)


@router.get("/contracts", response_model=List[ContractResponse])
async def list_contracts(contract_status: Optional[str] = None, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.list_contracts(db, current_user.tenant_id, contract_status)


@router.post("/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(payload: AssetCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.create_asset(db, current_user.tenant_id, payload)


@router.get("/assets", response_model=List[AssetResponse])
async def list_assets(customer_id: Optional[str] = None, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.list_assets(db, current_user.tenant_id, customer_id)


@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.create_ticket(db, current_user.tenant_id, payload)


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(ticket_status: Optional[str] = None, priority: Optional[str] = None, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.list_tickets(db, current_user.tenant_id, ticket_status, priority)


@router.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_status(ticket_id: str, payload: TicketStatusUpdate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.update_ticket_status(db, current_user.tenant_id, ticket_id, payload)


@router.post("/tickets/{ticket_id}/activities", status_code=status.HTTP_201_CREATED)
async def add_activity(ticket_id: str, payload: ActivityCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    activity = await ServiceManagementService.add_activity(db, current_user.tenant_id, ticket_id, payload)
    return {"id": activity.id, "ticket_id": activity.ticket_id, "hours": activity.hours, "billable": activity.billable}


@router.get("/summary", response_model=List[TicketSummary])
async def summary(current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceManagementService.summarize(db, current_user.tenant_id)


@router.post("/technicians", response_model=TechnicianResponse, status_code=status.HTTP_201_CREATED)
async def create_technician(payload: TechnicianCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await FieldService.create_technician(db, current_user.tenant_id, payload)


@router.get("/technicians", response_model=List[TechnicianResponse])
async def list_technicians(territory: Optional[str] = None, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await FieldService.list_technicians(db, current_user.tenant_id, territory)


@router.post("/dispatches", response_model=DispatchResponse, status_code=status.HTTP_201_CREATED)
async def create_dispatch(payload: DispatchCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await FieldService.create_dispatch(db, current_user.tenant_id, payload)


@router.get("/dispatches", response_model=List[DispatchResponse])
async def list_dispatches(from_date: Optional[str] = None, to_date: Optional[str] = None, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    from datetime import date
    return await FieldService.list_dispatches(db, current_user.tenant_id, date.fromisoformat(from_date) if from_date else None, date.fromisoformat(to_date) if to_date else None)


@router.patch("/dispatches/{dispatch_id}/status", response_model=DispatchResponse)
async def update_dispatch(dispatch_id: str, payload: DispatchStatusUpdate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await FieldService.update_dispatch(db, current_user.tenant_id, dispatch_id, payload)


@router.post("/maintenance-plans", response_model=MaintenancePlanResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_plan(payload: MaintenancePlanCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await PreventiveMaintenanceService.create_plan(db, current_user.tenant_id, payload)


@router.get("/maintenance-plans/due", response_model=List[MaintenancePlanResponse])
async def due_maintenance_plans(current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await PreventiveMaintenanceService.list_due_plans(db, current_user.tenant_id)


@router.post("/maintenance-plans/{plan_id}/complete", response_model=MaintenancePlanResponse)
async def complete_maintenance_plan(plan_id: str, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await PreventiveMaintenanceService.complete_plan(db, current_user.tenant_id, plan_id)


@router.post("/knowledge", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_article(payload: ArticleCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await KnowledgeService.create_article(db, current_user.tenant_id, payload)


@router.get("/knowledge/search", response_model=List[ArticleResponse])
async def search_knowledge(q: str, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await KnowledgeService.search(db, current_user.tenant_id, q)


@router.post("/knowledge/{article_id}/publish", response_model=ArticleResponse)
async def publish_knowledge(article_id: str, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await KnowledgeService.publish(db, current_user.tenant_id, article_id)


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(payload: FeedbackCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await CustomerExperienceService.submit_feedback(db, current_user.tenant_id, payload)


@router.get("/feedback/metrics")
async def feedback_metrics(current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await CustomerExperienceService.metrics(db, current_user.tenant_id)


@router.post("/charges", response_model=ChargeResponse, status_code=status.HTTP_201_CREATED)
async def create_service_charge(payload: ChargeCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceBillingService.create_charge(db, current_user.tenant_id, payload)


@router.get("/charges", response_model=List[ChargeResponse])
async def list_service_charges(charge_status: Optional[str] = None, ticket_id: Optional[str] = None, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceBillingService.list_charges(db, current_user.tenant_id, charge_status, ticket_id)


@router.patch("/charges/{charge_id}/status", response_model=ChargeResponse)
async def update_charge_status(charge_id: str, payload: ChargeStatusUpdate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceBillingService.update_charge_status(db, current_user.tenant_id, charge_id, payload)


@router.post("/invoice-batches", response_model=InvoiceBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice_batch(payload: InvoiceBatchCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await ServiceBillingService.create_batch(db, current_user.tenant_id, payload, current_user.id)


@router.post("/escalations/detect", response_model=List[EscalationResponse])
async def detect_sla_escalations(current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await SLAEscalationService.detect(db, current_user.tenant_id)


@router.get("/escalations", response_model=List[EscalationResponse])
async def list_sla_escalations(current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await SLAEscalationService.list_open(db, current_user.tenant_id)


@router.post("/escalations/{escalation_id}/acknowledge", response_model=EscalationResponse)
async def acknowledge_sla_escalation(escalation_id: str, payload: EscalationAcknowledge, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await SLAEscalationService.acknowledge(db, current_user.tenant_id, escalation_id, current_user.id, payload)


@router.post("/portal/tokens", response_model=PortalTokenResponse)
async def issue_portal_token(customer_id: str, label: str = "Portal", days: int = 30, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    raw_token, record = await CustomerPortalService.issue_token(db, current_user.tenant_id, customer_id, label, days)
    return {"token": raw_token, "expires_at": record.expires_at, "customer_id": record.customer_id, "label": record.label}


@router.post("/portal/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def request_portal_appointment(payload: AppointmentRequestCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await CustomerPortalService.request_appointment(db, current_user.tenant_id, payload)


@router.patch("/portal/appointments/{request_id}", response_model=AppointmentResponse)
async def review_portal_appointment(request_id: str, payload: AppointmentReview, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await CustomerPortalService.review_appointment(db, current_user.tenant_id, request_id, payload, current_user.id)


@router.post("/portal/messages", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def add_portal_message(payload: ConversationCreate, current_user: CurrentUser = Depends(manager()), db: AsyncSession = Depends(get_db_session)):
    return await CustomerPortalService.add_message(db, current_user.tenant_id, payload, "AGENT", current_user.id)


@router.get("/portal/tickets/{ticket_id}/messages", response_model=List[ConversationResponse])
async def list_portal_messages(ticket_id: str, current_user: CurrentUser = Depends(viewer()), db: AsyncSession = Depends(get_db_session)):
    return await CustomerPortalService.list_messages(db, current_user.tenant_id, ticket_id)
