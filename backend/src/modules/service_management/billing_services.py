"""Service charging, invoice batching, and SLA escalation logic."""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError
from .billing_models import ServiceCharge, ServiceInvoiceBatch, SLAEscalation
from .billing_schemas import ChargeCreate, ChargeStatusUpdate, EscalationAcknowledge, InvoiceBatchCreate
from .models import ServiceContract, ServiceTicket


MONEY = Decimal("0.01")


class ServiceBillingService:
    """Calculates auditable charges and creates invoice-ready batches."""

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return value.quantize(MONEY, rounding=ROUND_HALF_UP)

    @staticmethod
    async def _ticket(db: AsyncSession, tenant_id: str, ticket_id: str) -> ServiceTicket:
        result = await db.execute(select(ServiceTicket).where(ServiceTicket.id == ticket_id, ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise EntityNotFoundError("Service ticket not found")
        return ticket

    @classmethod
    async def create_charge(cls, db: AsyncSession, tenant_id: str, payload: ChargeCreate) -> ServiceCharge:
        ticket = await cls._ticket(db, tenant_id, payload.ticket_id)
        if payload.contract_id:
            contract = await db.get(ServiceContract, payload.contract_id)
            if not contract or contract.tenant_id != tenant_id:
                raise EntityNotFoundError("Service contract not found")
        gross = payload.quantity * payload.unit_price
        discount = cls._money(gross * payload.discount_percent / Decimal("100"))
        net = cls._money(gross - discount)
        tax = cls._money(net * payload.tax_percent / Decimal("100"))
        charge = ServiceCharge(tenant_id=tenant_id, net_amount=net, tax_amount=tax, total_amount=net + tax, status="DRAFT", **payload.model_dump())
        if not charge.contract_id:
            charge.contract_id = ticket.contract_id
        db.add(charge)
        await db.commit()
        await db.refresh(charge)
        return charge

    @classmethod
    async def list_charges(cls, db: AsyncSession, tenant_id: str, charge_status: Optional[str] = None, ticket_id: Optional[str] = None) -> List[ServiceCharge]:
        query = select(ServiceCharge).where(ServiceCharge.tenant_id == tenant_id, ServiceCharge.is_deleted == False).order_by(ServiceCharge.charge_date.desc(), ServiceCharge.created_at.desc())
        if charge_status:
            query = query.where(ServiceCharge.status == charge_status)
        if ticket_id:
            query = query.where(ServiceCharge.ticket_id == ticket_id)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def update_charge_status(cls, db: AsyncSession, tenant_id: str, charge_id: str, payload: ChargeStatusUpdate) -> ServiceCharge:
        result = await db.execute(select(ServiceCharge).where(ServiceCharge.id == charge_id, ServiceCharge.tenant_id == tenant_id, ServiceCharge.is_deleted == False))
        charge = result.scalar_one_or_none()
        if not charge:
            raise EntityNotFoundError("Service charge not found")
        transitions = {"DRAFT": {"APPROVED", "REJECTED", "VOID"}, "APPROVED": {"INVOICED", "VOID"}, "REJECTED": {"DRAFT", "VOID"}, "INVOICED": set(), "VOID": set()}
        if payload.status != charge.status and payload.status not in transitions.get(charge.status, set()):
            raise ValueError(f"Cannot transition charge from {charge.status} to {payload.status}")
        charge.status = payload.status
        await db.commit()
        await db.refresh(charge)
        return charge

    @classmethod
    async def create_batch(cls, db: AsyncSession, tenant_id: str, payload: InvoiceBatchCreate, user_id: str) -> ServiceInvoiceBatch:
        query = select(ServiceCharge).where(ServiceCharge.tenant_id == tenant_id, ServiceCharge.is_deleted == False, ServiceCharge.status == "APPROVED", ServiceCharge.charge_date >= payload.period_start, ServiceCharge.charge_date <= payload.period_end, ServiceCharge.currency == payload.currency)
        if payload.customer_id:
            query = query.join(ServiceTicket, ServiceTicket.id == ServiceCharge.ticket_id).where(ServiceTicket.customer_id == payload.customer_id)
        charges = list((await db.execute(query)).scalars().all())
        if not charges:
            raise ValueError("No approved charges found for invoice period")
        net = sum((charge.net_amount for charge in charges), Decimal("0"))
        tax = sum((charge.tax_amount for charge in charges), Decimal("0"))
        previous = await db.execute(select(ServiceInvoiceBatch).where(ServiceInvoiceBatch.tenant_id == tenant_id).order_by(ServiceInvoiceBatch.batch_number.desc()).limit(1))
        latest = previous.scalar_one_or_none()
        sequence = 1
        if latest:
            try:
                sequence = int(latest.batch_number.rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                pass
        batch = ServiceInvoiceBatch(tenant_id=tenant_id, batch_number=f"SIB-{datetime.now(timezone.utc).year}-{sequence:05d}", charge_count=len(charges), net_amount=net, tax_amount=tax, total_amount=net + tax, status="DRAFT", **payload.model_dump())
        db.add(batch)
        await db.flush()
        for charge in charges:
            charge.status = "INVOICED"
            charge.invoice_id = batch.id
        await db.commit()
        await db.refresh(batch)
        return batch


class SLAEscalationService:
    """Detects SLA risk and records acknowledgement history."""

    @staticmethod
    def _aware(value: datetime) -> datetime:
        """Treat SQLite's timezone-stripped values as UTC for SLA arithmetic."""
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

    @classmethod
    async def detect(cls, db: AsyncSession, tenant_id: str, threshold_percent: Decimal = Decimal("80")) -> List[SLAEscalation]:
        now = datetime.now(timezone.utc)
        result = await db.execute(select(ServiceTicket).where(ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False, ServiceTicket.status.in_(["OPEN", "IN_PROGRESS", "WAITING_CUSTOMER"]), ServiceTicket.due_at.is_not(None), ServiceTicket.due_at > ServiceTicket.opened_at))
        escalations = []
        for ticket in result.scalars().all():
            opened_at = cls._aware(ticket.opened_at)
            due_at = cls._aware(ticket.due_at)
            duration = (due_at - opened_at).total_seconds()
            elapsed = (now - opened_at).total_seconds()
            percent = Decimal(str(max(0, min(100, elapsed / duration * 100))))
            if percent < threshold_percent:
                continue
            existing = await db.execute(select(SLAEscalation).where(SLAEscalation.tenant_id == tenant_id, SLAEscalation.ticket_id == ticket.id, SLAEscalation.status == "OPEN"))
            if existing.scalar_one_or_none():
                continue
            escalation = SLAEscalation(tenant_id=tenant_id, ticket_id=ticket.id, contract_id=ticket.contract_id, escalation_level="L1" if percent < 100 else "L2", trigger="BREACH" if percent >= 100 else "AT_RISK", threshold_percent=percent.quantize(Decimal("0.01")), detected_at=now, status="OPEN")
            db.add(escalation)
            escalations.append(escalation)
        if escalations:
            await db.commit()
            for escalation in escalations:
                await db.refresh(escalation)
        return escalations

    @classmethod
    async def acknowledge(cls, db: AsyncSession, tenant_id: str, escalation_id: str, user_id: str, payload: EscalationAcknowledge) -> SLAEscalation:
        result = await db.execute(select(SLAEscalation).where(SLAEscalation.id == escalation_id, SLAEscalation.tenant_id == tenant_id, SLAEscalation.is_deleted == False))
        escalation = result.scalar_one_or_none()
        if not escalation:
            raise EntityNotFoundError("SLA escalation not found")
        if escalation.status != "OPEN":
            raise ValueError("Only open escalations can be acknowledged")
        escalation.status = "ACKNOWLEDGED"
        escalation.acknowledged_at = datetime.now(timezone.utc)
        escalation.acknowledged_by_id = user_id
        escalation.notes = payload.notes
        await db.commit()
        await db.refresh(escalation)
        return escalation

    @classmethod
    async def list_open(cls, db: AsyncSession, tenant_id: str) -> List[SLAEscalation]:
        result = await db.execute(select(SLAEscalation).where(SLAEscalation.tenant_id == tenant_id, SLAEscalation.is_deleted == False, SLAEscalation.status == "OPEN").order_by(SLAEscalation.detected_at.asc()))
        return list(result.scalars().all())
