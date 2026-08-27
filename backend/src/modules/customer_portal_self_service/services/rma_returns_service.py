"""
Customer RMA Returns & Self-Service Support Routing Service.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.audit import AuditService
from ..models import CustomerSupportTicket, CustomerRMARequest
from ..schemas import SupportTicketCreate, RMARequestCreate

class RMAReturnsService:
    @staticmethod
    async def create_rma(
        session: AsyncSession,
        payload: RMARequestCreate,
        tenant_id: str,
        actor_id: str
    ) -> CustomerRMARequest:
        rma_num = f"RMA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        rma = CustomerRMARequest(
            tenant_id=tenant_id,
            rma_number=rma_num,
            customer_account_id=payload.customer_account_id,
            original_sales_order_id=payload.original_sales_order_id,
            item_id=payload.item_id,
            quantity_to_return=payload.quantity_to_return,
            return_reason=payload.return_reason,
            status="REQUESTED"
        )
        session.add(rma)
        await session.commit()
        await session.refresh(rma)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_RMA",
            entity_type="CustomerRMARequest",
            entity_id=rma.id,
            description=f"Created return authorization #{rma_num}"
        )
        return rma
