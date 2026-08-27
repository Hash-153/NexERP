"""Customer portal operations with hashed token persistence."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError
from .models import ServiceTicket
from .portal_models import AppointmentRequest, PortalAccessToken, PortalConversation
from .portal_schemas import AppointmentRequestCreate, AppointmentReview, ConversationCreate


class CustomerPortalService:
    """Provides customer-safe service interactions without exposing raw tokens."""

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    async def _ticket(db: AsyncSession, tenant_id: str, ticket_id: str) -> ServiceTicket:
        result = await db.execute(select(ServiceTicket).where(ServiceTicket.id == ticket_id, ServiceTicket.tenant_id == tenant_id, ServiceTicket.is_deleted == False))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise EntityNotFoundError("Service ticket not found")
        return ticket

    @classmethod
    async def issue_token(cls, db: AsyncSession, tenant_id: str, customer_id: str, label: str = "Portal", days: int = 30) -> tuple[str, PortalAccessToken]:
        if not 1 <= days <= 365:
            raise ValueError("Portal token lifetime must be between 1 and 365 days")
        raw_token = secrets.token_urlsafe(32)
        record = PortalAccessToken(tenant_id=tenant_id, customer_id=customer_id, token_hash=cls._hash(raw_token), expires_at=datetime.now(timezone.utc) + timedelta(days=days), label=label)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return raw_token, record

    @classmethod
    async def validate_token(cls, db: AsyncSession, tenant_id: str, raw_token: str) -> PortalAccessToken:
        result = await db.execute(select(PortalAccessToken).where(PortalAccessToken.tenant_id == tenant_id, PortalAccessToken.token_hash == cls._hash(raw_token), PortalAccessToken.revoked_at.is_(None)))
        record = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        expires_at = record.expires_at.replace(tzinfo=timezone.utc) if record and record.expires_at.tzinfo is None else record.expires_at if record else None
        if not record or expires_at <= now:
            raise ValueError("Portal token is invalid or expired")
        record.last_used_at = now
        await db.commit()
        return record

    @classmethod
    async def request_appointment(cls, db: AsyncSession, tenant_id: str, payload: AppointmentRequestCreate) -> AppointmentRequest:
        ticket = await cls._ticket(db, tenant_id, payload.ticket_id)
        if ticket.customer_id and ticket.customer_id != payload.customer_id:
            raise ValueError("Customer cannot request an appointment for another customer's ticket")
        request = AppointmentRequest(tenant_id=tenant_id, status="REQUESTED", **payload.model_dump())
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    @classmethod
    async def review_appointment(cls, db: AsyncSession, tenant_id: str, request_id: str, payload: AppointmentReview, reviewer_id: str) -> AppointmentRequest:
        result = await db.execute(select(AppointmentRequest).where(AppointmentRequest.id == request_id, AppointmentRequest.tenant_id == tenant_id, AppointmentRequest.is_deleted == False))
        request = result.scalar_one_or_none()
        if not request:
            raise EntityNotFoundError("Appointment request not found")
        if request.status != "REQUESTED":
            raise ValueError("Only requested appointments can be reviewed")
        request.status = payload.status
        request.review_notes = payload.review_notes
        request.reviewed_by_id = reviewer_id
        request.reviewed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(request)
        return request

    @classmethod
    async def add_message(cls, db: AsyncSession, tenant_id: str, payload: ConversationCreate, author_type: str, author_id: str | None = None) -> PortalConversation:
        ticket = await cls._ticket(db, tenant_id, payload.ticket_id)
        if ticket.customer_id and ticket.customer_id != payload.customer_id:
            raise ValueError("Customer cannot message another customer's ticket")
        message = PortalConversation(tenant_id=tenant_id, author_type=author_type, author_id=author_id, sent_at=datetime.now(timezone.utc), is_internal=author_type == "AGENT", attachment_count=str(payload.attachment_count), ticket_id=payload.ticket_id, customer_id=payload.customer_id, message=payload.message)
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @classmethod
    async def list_messages(cls, db: AsyncSession, tenant_id: str, ticket_id: str) -> List[PortalConversation]:
        await cls._ticket(db, tenant_id, ticket_id)
        result = await db.execute(select(PortalConversation).where(PortalConversation.tenant_id == tenant_id, PortalConversation.ticket_id == ticket_id, PortalConversation.is_deleted == False, PortalConversation.is_internal == False).order_by(PortalConversation.sent_at.asc()))
        return list(result.scalars().all())
