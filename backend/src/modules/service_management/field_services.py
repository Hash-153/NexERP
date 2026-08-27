"""Field service scheduling and customer-experience operations."""

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError
from .field_models import CustomerFeedback, DispatchOrder, KnowledgeArticle, MaintenancePlan, ServiceTechnician
from .field_schemas import ArticleCreate, DispatchCreate, DispatchStatusUpdate, FeedbackCreate, MaintenancePlanCreate, TechnicianCreate
from .models import ServiceTicket


class FieldService:
    """Owns technician capacity, dispatch commitments, and preventive plans."""

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    async def ticket(db: AsyncSession, tenant_id: str, ticket_id: str) -> ServiceTicket:
        result = await db.execute(select(ServiceTicket).where(ServiceTicket.id == ticket_id, ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise EntityNotFoundError("Service ticket not found")
        return ticket

    @classmethod
    async def create_technician(cls, db: AsyncSession, tenant_id: str, payload: TechnicianCreate) -> ServiceTechnician:
        technician = ServiceTechnician(tenant_id=tenant_id, status="AVAILABLE", **payload.model_dump())
        db.add(technician)
        await db.commit()
        await db.refresh(technician)
        return technician

    @classmethod
    async def list_technicians(cls, db: AsyncSession, tenant_id: str, territory: Optional[str] = None) -> List[ServiceTechnician]:
        query = select(ServiceTechnician).where(ServiceTechnician.tenant_id == tenant_id, ServiceTechnician.is_deleted == False).order_by(ServiceTechnician.display_name.asc())
        if territory:
            query = query.where(ServiceTechnician.territory == territory)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def create_dispatch(cls, db: AsyncSession, tenant_id: str, payload: DispatchCreate) -> DispatchOrder:
        await cls.ticket(db, tenant_id, payload.ticket_id)
        if payload.technician_id:
            tech = await db.get(ServiceTechnician, payload.technician_id)
            if not tech or tech.tenant_id != tenant_id or tech.is_deleted:
                raise EntityNotFoundError("Technician not found")
            conflict = await db.execute(select(DispatchOrder).where(DispatchOrder.tenant_id == tenant_id, DispatchOrder.technician_id == payload.technician_id, DispatchOrder.status.in_(["PLANNED", "CONFIRMED", "EN_ROUTE", "ON_SITE"]), DispatchOrder.scheduled_start < payload.scheduled_end, DispatchOrder.scheduled_end > payload.scheduled_start))
            if conflict.scalar_one_or_none():
                raise ValueError("Technician already has a dispatch in this time window")
        result = await db.execute(select(DispatchOrder).where(DispatchOrder.tenant_id == tenant_id).order_by(DispatchOrder.dispatch_number.desc()).limit(1))
        latest = result.scalar_one_or_none()
        sequence = 1
        if latest:
            try:
                sequence = int(latest.dispatch_number.rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                pass
        dispatch = DispatchOrder(tenant_id=tenant_id, dispatch_number=f"DSP-{cls.now().year}-{sequence:05d}", status="PLANNED", **payload.model_dump())
        db.add(dispatch)
        await db.commit()
        await db.refresh(dispatch)
        return dispatch

    @classmethod
    async def list_dispatches(cls, db: AsyncSession, tenant_id: str, from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[DispatchOrder]:
        query = select(DispatchOrder).where(DispatchOrder.tenant_id == tenant_id, DispatchOrder.is_deleted == False).order_by(DispatchOrder.scheduled_start.asc())
        if from_date:
            query = query.where(DispatchOrder.scheduled_start >= datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc))
        if to_date:
            query = query.where(DispatchOrder.scheduled_start < datetime.combine(to_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc))
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def update_dispatch(cls, db: AsyncSession, tenant_id: str, dispatch_id: str, payload: DispatchStatusUpdate) -> DispatchOrder:
        result = await db.execute(select(DispatchOrder).where(DispatchOrder.id == dispatch_id, DispatchOrder.tenant_id == tenant_id, DispatchOrder.is_deleted == False))
        dispatch = result.scalar_one_or_none()
        if not dispatch:
            raise EntityNotFoundError("Dispatch order not found")
        valid = {"PLANNED": {"CONFIRMED", "CANCELLED"}, "CONFIRMED": {"EN_ROUTE", "CANCELLED"}, "EN_ROUTE": {"ON_SITE", "CANCELLED"}, "ON_SITE": {"COMPLETED", "CANCELLED"}, "COMPLETED": set(), "CANCELLED": set()}
        if payload.status != dispatch.status and payload.status not in valid.get(dispatch.status, set()):
            raise ValueError(f"Cannot transition dispatch from {dispatch.status} to {payload.status}")
        if payload.status == "ON_SITE":
            dispatch.actual_start = cls.now()
            dispatch.arrival_notes = payload.notes
        if payload.status == "COMPLETED":
            dispatch.actual_end = cls.now()
            dispatch.completion_notes = payload.notes
        dispatch.status = payload.status
        await db.commit()
        await db.refresh(dispatch)
        return dispatch


class PreventiveMaintenanceService:
    """Creates and advances asset maintenance schedules."""

    @classmethod
    async def create_plan(cls, db: AsyncSession, tenant_id: str, payload: MaintenancePlanCreate) -> MaintenancePlan:
        plan = MaintenancePlan(tenant_id=tenant_id, status="ACTIVE", **payload.model_dump())
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan

    @classmethod
    async def list_due_plans(cls, db: AsyncSession, tenant_id: str, as_of: Optional[date] = None) -> List[MaintenancePlan]:
        due_date = as_of or date.today()
        result = await db.execute(select(MaintenancePlan).where(MaintenancePlan.tenant_id == tenant_id, MaintenancePlan.is_deleted == False, MaintenancePlan.status == "ACTIVE", MaintenancePlan.next_due_date <= due_date).order_by(MaintenancePlan.next_due_date.asc()))
        return list(result.scalars().all())

    @classmethod
    async def complete_plan(cls, db: AsyncSession, tenant_id: str, plan_id: str, completed_date: Optional[date] = None) -> MaintenancePlan:
        result = await db.execute(select(MaintenancePlan).where(MaintenancePlan.id == plan_id, MaintenancePlan.tenant_id == tenant_id, MaintenancePlan.is_deleted == False))
        plan = result.scalar_one_or_none()
        if not plan:
            raise EntityNotFoundError("Maintenance plan not found")
        completed = completed_date or date.today()
        plan.last_completed_date = completed
        plan.next_due_date = completed + timedelta(days=plan.frequency_days)
        await db.commit()
        await db.refresh(plan)
        return plan


class KnowledgeService:
    """Publishes and searches controlled service resolution content."""

    @classmethod
    async def create_article(cls, db: AsyncSession, tenant_id: str, payload: ArticleCreate) -> KnowledgeArticle:
        article = KnowledgeArticle(tenant_id=tenant_id, status="DRAFT", version=1, view_count=0, helpful_count=0, **payload.model_dump())
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    @classmethod
    async def search(cls, db: AsyncSession, tenant_id: str, phrase: str) -> List[KnowledgeArticle]:
        term = f"%{phrase.strip()}%"
        result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.tenant_id == tenant_id, KnowledgeArticle.is_deleted == False, KnowledgeArticle.status == "PUBLISHED", KnowledgeArticle.title.ilike(term) | KnowledgeArticle.body.ilike(term)).order_by(KnowledgeArticle.helpful_count.desc(), KnowledgeArticle.view_count.desc()))
        articles = list(result.scalars().all())
        for article in articles:
            article.view_count += 1
        if articles:
            await db.commit()
        return articles

    @classmethod
    async def publish(cls, db: AsyncSession, tenant_id: str, article_id: str) -> KnowledgeArticle:
        result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id, KnowledgeArticle.tenant_id == tenant_id, KnowledgeArticle.is_deleted == False))
        article = result.scalar_one_or_none()
        if not article:
            raise EntityNotFoundError("Knowledge article not found")
        article.status = "PUBLISHED"
        article.published_at = cls._now()
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)


class CustomerExperienceService:
    """Records bounded customer feedback and computes service quality metrics."""

    @classmethod
    async def submit_feedback(cls, db: AsyncSession, tenant_id: str, payload: FeedbackCreate) -> CustomerFeedback:
        ticket_result = await db.execute(select(ServiceTicket).where(ServiceTicket.id == payload.ticket_id, ServiceTicket.tenant_id == tenant_id, ServiceTicket.status.in_(["RESOLVED", "CLOSED"])))
        if not ticket_result.scalar_one_or_none():
            raise ValueError("Feedback can only be submitted for resolved or closed tickets")
        feedback = CustomerFeedback(tenant_id=tenant_id, submitted_at=datetime.now(timezone.utc), **payload.model_dump())
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback

    @classmethod
    async def metrics(cls, db: AsyncSession, tenant_id: str) -> dict:
        result = await db.execute(select(func.count(CustomerFeedback.id), func.coalesce(func.avg(CustomerFeedback.rating), 0), func.coalesce(func.avg(CustomerFeedback.response_time_rating), 0), func.coalesce(func.avg(CustomerFeedback.resolution_rating), 0)).where(CustomerFeedback.tenant_id == tenant_id, CustomerFeedback.is_deleted == False))
        count, rating, response, resolution = result.one()
        return {"response_count": count, "average_rating": round(float(rating), 2), "average_response_rating": round(float(response), 2), "average_resolution_rating": round(float(resolution), 2)}
