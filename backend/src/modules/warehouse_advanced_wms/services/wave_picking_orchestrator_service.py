"""
Wave Picking Orchestration Service.
Groups disparate customer orders into synchronized pick waves for optimized travel paths.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from backend.src.core.audit import AuditService
from ..models import WaveBatchRun, WavePickTask, WarehouseLocation
from ..schemas import WaveBatchCreate, PickExecutionRequest

class WavePickingOrchestratorService:
    @staticmethod
    async def release_wave(
        session: AsyncSession,
        payload: WaveBatchCreate,
        tenant_id: str,
        actor_id: str
    ) -> WaveBatchRun:
        if not payload.order_ids:
            raise BusinessRuleViolationError("Cannot create a wave with zero orders.")

        wave = WaveBatchRun(
            tenant_id=tenant_id,
            wave_number=f"WAVE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:4].upper()}",
            carrier_cutoff_time=payload.carrier_cutoff_time,
            priority_level=payload.priority_level,
            status="RELEASED",
            total_lines=len(payload.order_ids) * 3,  # simulated lines per order
            picked_lines=0
        )
        session.add(wave)
        await session.flush()

        # Find available pick face locations
        loc_stmt = select(WarehouseLocation).where(
            WarehouseLocation.tenant_id == tenant_id,
            WarehouseLocation.is_pick_face == True
        ).limit(10)
        loc_res = await session.execute(loc_stmt)
        locations = loc_res.scalars().all()

        for idx, order_id in enumerate(payload.order_ids):
            loc_id = locations[idx % len(locations)].id if locations else str(uuid.uuid4())
            task = WavePickTask(
                tenant_id=tenant_id,
                wave_id=wave.id,
                sales_order_id=order_id,
                item_id=str(uuid.uuid4()),
                location_id=loc_id,
                requested_qty=Decimal("5.0"),
                picked_qty=Decimal("0.0"),
                sequence_order=idx + 1,
                status="PENDING"
            )
            session.add(task)

        await session.commit()
        await session.refresh(wave)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="RELEASE_WAVE",
            entity_type="WaveBatchRun",
            entity_id=wave.id,
            description=f"Released wave {wave.wave_number} with {len(payload.order_ids)} orders."
        )
        return wave

    @staticmethod
    async def record_pick_completion(
        session: AsyncSession,
        payload: PickExecutionRequest,
        tenant_id: str,
        actor_id: str
    ) -> WavePickTask:
        stmt = select(WavePickTask).where(
            WavePickTask.id == payload.task_id,
            WavePickTask.tenant_id == tenant_id
        )
        res = await session.execute(stmt)
        task = res.scalar_one_or_none()
        if not task:
            raise EntityNotFoundError("Pick task not found.")

        task.picked_qty = payload.picked_qty
        task.scanned_barcode = payload.scanned_barcode
        task.tote_license_plate = payload.tote_license_plate
        task.status = "COMPLETED"

        # Update parent wave picked lines
        wave_stmt = select(WaveBatchRun).where(WaveBatchRun.id == task.wave_id)
        w_res = await session.execute(wave_stmt)
        wave = w_res.scalar_one_or_none()
        if wave:
            wave.picked_lines += 1
            if wave.picked_lines >= wave.total_lines:
                wave.status = "COMPLETED"

        await session.commit()
        await session.refresh(task)
        return task
