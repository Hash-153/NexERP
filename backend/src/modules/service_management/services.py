"""Transactional service-management operations."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.src.core.exceptions import EntityNotFoundError
from .models import CustomerAsset, ServiceActivity, ServiceContract, ServiceTicket
from .schemas import ActivityCreate, AssetCreate, ContractCreate, TicketCreate, TicketStatusUpdate


class ServiceManagementService:
    """Coordinates support desk, contract, asset, and field-work transactions."""

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    async def _next_number(db: AsyncSession, tenant_id: str, model, field: str, prefix: str) -> str:
        result = await db.execute(select(model).where(model.tenant_id == tenant_id).order_by(getattr(model, field).desc()).limit(1))
        latest = result.scalar_one_or_none()
        sequence = 1
        if latest:
            try:
                sequence = int(getattr(latest, field).rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                sequence = 1
        return f"{prefix}-{datetime.now(timezone.utc).year}-{sequence:05d}"

    @classmethod
    async def create_contract(cls, db: AsyncSession, tenant_id: str, payload: ContractCreate) -> ServiceContract:
        contract = ServiceContract(tenant_id=tenant_id, status="ACTIVE", consumed_hours=0, **payload.model_dump())
        db.add(contract)
        await db.commit()
        await db.refresh(contract)
        return contract

    @classmethod
    async def create_asset(cls, db: AsyncSession, tenant_id: str, payload: AssetCreate) -> CustomerAsset:
        asset = CustomerAsset(tenant_id=tenant_id, status="ACTIVE", **payload.model_dump())
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset

    @classmethod
    async def create_ticket(cls, db: AsyncSession, tenant_id: str, payload: TicketCreate) -> ServiceTicket:
        now = cls._now()
        due_at = None
        if payload.contract_id:
            contract = await cls.get_contract(db, tenant_id, payload.contract_id)
            from datetime import timedelta
            due_at = now + timedelta(hours=float(contract.response_hours))
        ticket_number = await cls._next_number(db, tenant_id, ServiceTicket, "ticket_number", "TKT")
        ticket = ServiceTicket(tenant_id=tenant_id, ticket_number=ticket_number, opened_at=now, due_at=due_at, status="OPEN", actual_hours=0, **payload.model_dump())
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket

    @staticmethod
    async def get_contract(db: AsyncSession, tenant_id: str, contract_id: str) -> ServiceContract:
        result = await db.execute(select(ServiceContract).where(ServiceContract.id == contract_id, ServiceContract.tenant_id == tenant_id, ServiceContract.is_deleted == False))
        contract = result.scalar_one_or_none()
        if not contract:
            raise EntityNotFoundError("Service contract not found")
        return contract

    @staticmethod
    async def get_ticket(db: AsyncSession, tenant_id: str, ticket_id: str) -> ServiceTicket:
        result = await db.execute(select(ServiceTicket).where(ServiceTicket.id == ticket_id, ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False).options(selectinload(ServiceTicket.activities)))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise EntityNotFoundError("Service ticket not found")
        return ticket

    @classmethod
    async def list_contracts(cls, db: AsyncSession, tenant_id: str, status: Optional[str] = None) -> List[ServiceContract]:
        query = select(ServiceContract).where(ServiceContract.tenant_id == tenant_id, ServiceContract.is_deleted == False).order_by(ServiceContract.end_date.asc())
        if status:
            query = query.where(ServiceContract.status == status)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def list_assets(cls, db: AsyncSession, tenant_id: str, customer_id: Optional[str] = None) -> List[CustomerAsset]:
        query = select(CustomerAsset).where(CustomerAsset.tenant_id == tenant_id, CustomerAsset.is_deleted == False).order_by(CustomerAsset.asset_number.asc())
        if customer_id:
            query = query.where(CustomerAsset.customer_id == customer_id)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def list_tickets(cls, db: AsyncSession, tenant_id: str, status: Optional[str] = None, priority: Optional[str] = None) -> List[ServiceTicket]:
        query = select(ServiceTicket).where(ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False).order_by(ServiceTicket.opened_at.desc())
        if status:
            query = query.where(ServiceTicket.status == status)
        if priority:
            query = query.where(ServiceTicket.priority == priority)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def update_ticket_status(cls, db: AsyncSession, tenant_id: str, ticket_id: str, payload: TicketStatusUpdate) -> ServiceTicket:
        ticket = await cls.get_ticket(db, tenant_id, ticket_id)
        now = cls._now()
        allowed = {"OPEN": {"IN_PROGRESS", "CANCELLED"}, "IN_PROGRESS": {"WAITING_CUSTOMER", "RESOLVED", "CANCELLED"}, "WAITING_CUSTOMER": {"IN_PROGRESS", "CANCELLED"}, "RESOLVED": {"CLOSED", "IN_PROGRESS"}, "CLOSED": set(), "CANCELLED": set()}
        if payload.status != ticket.status and payload.status not in allowed.get(ticket.status, set()):
            raise ValueError(f"Cannot transition ticket from {ticket.status} to {payload.status}")
        if payload.status == "IN_PROGRESS" and ticket.first_response_at is None:
            ticket.first_response_at = now
        if payload.status == "RESOLVED":
            ticket.resolved_at = now
        ticket.status = payload.status
        ticket.resolution_notes = payload.resolution_notes or ticket.resolution_notes
        await db.commit()
        await db.refresh(ticket)
        return ticket

    @classmethod
    async def add_activity(cls, db: AsyncSession, tenant_id: str, ticket_id: str, payload: ActivityCreate) -> ServiceActivity:
        ticket = await cls.get_ticket(db, tenant_id, ticket_id)
        hours = payload.hours
        if hours is None and payload.ended_at:
            hours = Decimal(str((payload.ended_at - payload.started_at).total_seconds() / 3600)).quantize(Decimal("0.01"))
        activity = ServiceActivity(ticket_id=ticket.id, tenant_id=tenant_id, hours=hours or 0, **payload.model_dump(exclude={"hours"}))
        ticket.actual_hours = (ticket.actual_hours or 0) + activity.hours
        if ticket.contract_id:
            contract = await cls.get_contract(db, tenant_id, ticket.contract_id)
            contract.consumed_hours = (contract.consumed_hours or 0) + activity.hours
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return activity

    @classmethod
    async def summarize(cls, db: AsyncSession, tenant_id: str) -> List[dict]:
        result = await db.execute(select(ServiceTicket.status, ServiceTicket.priority, func.count(ServiceTicket.id), func.coalesce(func.sum(ServiceTicket.actual_hours), 0)).where(ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False).group_by(ServiceTicket.status, ServiceTicket.priority))
        now = cls._now()
        summaries = []
        for status, priority, count, hours in result.all():
            overdue_query = select(func.count(ServiceTicket.id)).where(ServiceTicket.tenant_id == tenant_id, ServiceTicket.status.in_(["OPEN", "IN_PROGRESS", "WAITING_CUSTOMER"]), ServiceTicket.due_at < now, ServiceTicket.status == status, ServiceTicket.priority == priority)
            overdue = (await db.execute(overdue_query)).scalar_one()
            summaries.append({"status": status, "priority": priority, "ticket_count": count, "total_hours": hours, "overdue_count": overdue})
        return summaries
