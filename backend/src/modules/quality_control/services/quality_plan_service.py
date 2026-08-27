"""
NexERP Quality Inspection Plan Management Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.quality_control.models import QualityInspectionPlan, QualityParameter
from backend.src.modules.quality_control.schemas import QualityPlanCreate


class QualityPlanService:
    """
    Quality template plan management.
    """

    @classmethod
    async def create_plan(cls, db: AsyncSession, tenant_id: str, payload: QualityPlanCreate) -> QualityInspectionPlan:
        query = select(QualityInspectionPlan).where(
            QualityInspectionPlan.tenant_id == tenant_id,
            QualityInspectionPlan.code == payload.code.upper().strip(),
            QualityInspectionPlan.is_deleted == False
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Inspection plan '{payload.code}' already exists.")

        plan = QualityInspectionPlan(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            item_id=payload.item_id,
            inspection_type=payload.inspection_type.value,
            sample_size_percentage=payload.sample_size_percentage,
            pass_threshold_percentage=payload.pass_threshold_percentage
        )
        db.add(plan)
        await db.flush()

        for param in payload.parameters:
            q_param = QualityParameter(
                tenant_id=tenant_id,
                inspection_plan_id=plan.id,
                parameter_name=param.parameter_name.strip(),
                test_type=param.test_type.value,
                min_value=param.min_value,
                max_value=param.max_value,
                target_value=param.target_value,
                is_critical=param.is_critical
            )
            db.add(q_param)

        await db.commit()
        await db.refresh(plan)
        return plan

    @classmethod
    async def list_plans(cls, db: AsyncSession, tenant_id: str) -> List[QualityInspectionPlan]:
        query = (
            select(QualityInspectionPlan)
            .where(QualityInspectionPlan.tenant_id == tenant_id, QualityInspectionPlan.is_deleted == False)
            .options(selectinload(QualityInspectionPlan.parameters))
            .order_by(QualityInspectionPlan.code.asc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
