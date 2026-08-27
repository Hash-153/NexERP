"""
Field Service Dispatch & Dynamic Assignment Service.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.core.audit import AuditService
from ..models import ServiceTechnician, FieldWorkOrder
from ..schemas import FieldWorkOrderCreate, DispatchAssignRequest

class DispatchSchedulingService:
    @staticmethod
    async def create_work_order(
        session: AsyncSession,
        payload: FieldWorkOrderCreate,
        tenant_id: str,
        actor_id: str
    ) -> FieldWorkOrder:
        order_num = f"FSO-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:4].upper()}"
        wo = FieldWorkOrder(
            tenant_id=tenant_id,
            order_number=order_num,
            customer_account_id=payload.customer_account_id,
            site_location_address=payload.site_location_address,
            asset_serial_number=payload.asset_serial_number,
            priority=payload.priority,
            status="UNASSIGNED",
            sla_severity=payload.sla_severity,
            scheduled_start=payload.scheduled_start,
            scheduled_end=payload.scheduled_end,
            issue_description=payload.issue_description
        )
        session.add(wo)
        await session.commit()
        await session.refresh(wo)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_WORK_ORDER",
            entity_type="FieldWorkOrder",
            entity_id=wo.id,
            description=f"Created work order {order_num} priority {payload.priority}"
        )
        return wo

    @staticmethod
    async def dispatch_technician(
        session: AsyncSession,
        payload: DispatchAssignRequest,
        tenant_id: str,
        actor_id: str
    ) -> FieldWorkOrder:
        stmt = select(FieldWorkOrder).where(
            FieldWorkOrder.id == payload.work_order_id,
            FieldWorkOrder.tenant_id == tenant_id
        )
        res = await session.execute(stmt)
        wo = res.scalar_one_or_none()
        if not wo:
            raise EntityNotFoundError("Work order not found.")

        tech_stmt = select(ServiceTechnician).where(
            ServiceTechnician.id == payload.technician_id,
            ServiceTechnician.tenant_id == tenant_id
        )
        t_res = await session.execute(tech_stmt)
        tech = t_res.scalar_one_or_none()
        if not tech:
            raise EntityNotFoundError("Technician not found.")

        wo.technician_id = tech.id
        wo.status = "DISPATCHED"

        await session.commit()
        await session.refresh(wo)
        return wo
