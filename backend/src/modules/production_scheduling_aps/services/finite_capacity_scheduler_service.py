"""
Finite Capacity Scheduling (APS) Heuristic Engine.
"""
from datetime import timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.audit import AuditService
from ..models import ProductionWorkCenterResource, ScheduledManufacturingOperation
from ..schemas import WorkCenterResourceCreate, ScheduledOperationInput

class FiniteCapacitySchedulerService:
    @staticmethod
    async def schedule_operation(
        session: AsyncSession,
        payload: ScheduledOperationInput,
        tenant_id: str,
        actor_id: str
    ) -> ScheduledManufacturingOperation:
        total_hours = payload.setup_hours + payload.run_hours
        end_time = payload.planned_start_time + timedelta(hours=float(total_hours))

        op = ScheduledManufacturingOperation(
            tenant_id=tenant_id,
            work_center_id=payload.work_center_id,
            work_order_number=payload.work_order_number,
            operation_sequence=payload.operation_sequence,
            operation_name=payload.operation_name,
            setup_hours=payload.setup_hours,
            run_hours=payload.run_hours,
            total_planned_hours=total_hours,
            planned_start_time=payload.planned_start_time,
            planned_end_time=end_time,
            status="SCHEDULED"
        )
        session.add(op)
        await session.commit()
        await session.refresh(op)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="SCHEDULE_OPERATION",
            entity_type="ScheduledManufacturingOperation",
            entity_id=op.id,
            description=f"Scheduled {op.work_order_number} op '{op.operation_name}' ({total_hours}h)"
        )
        return op
