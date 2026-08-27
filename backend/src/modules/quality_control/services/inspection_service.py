"""
NexERP Quality Inspection Execution & AQL Compliance Engine.
Evaluates parameter measurements against tolerance criteria and computes overall lot conformity.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.quality_control.models import (
    QualityInspectionPlan,
    QualityParameter,
    InspectionRecord,
    InspectionResultLine
)
from backend.src.modules.quality_control.schemas import InspectionRecordCreate
from backend.src.modules.quality_control.enums import InspectionStatus, TestType


class InspectionService:
    """
    Quality inspection execution and compliance evaluation service.
    """

    @classmethod
    async def generate_inspection_number(cls, db: AsyncSession, tenant_id: str, insp_date: date) -> str:
        year_str = str(insp_date.year)
        prefix = f"QC-{year_str}-"
        query = select(InspectionRecord).where(InspectionRecord.tenant_id == tenant_id).order_by(InspectionRecord.inspection_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.inspection_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def execute_inspection(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: InspectionRecordCreate,
        user_id: Optional[str] = None
    ) -> InspectionRecord:
        """
        Record inspection test readings, determine parameter conformance, and assign lot status.
        """
        plan_query = (
            select(QualityInspectionPlan)
            .where(QualityInspectionPlan.id == payload.plan_id, QualityInspectionPlan.tenant_id == tenant_id)
            .options(selectinload(QualityInspectionPlan.parameters))
        )
        p_res = await db.execute(plan_query)
        plan = p_res.scalar_one_or_none()

        if not plan:
            raise EntityNotFoundError("Quality inspection plan not found.")

        params_map = {p.id: p for p in plan.parameters}
        insp_num = await cls.generate_inspection_number(db, tenant_id, payload.inspection_date)

        # Check overall pass percentage
        pass_ratio = (payload.passed_quantity / payload.inspected_quantity) * Decimal("100.0") if payload.inspected_quantity > 0 else Decimal("0.0")
        has_critical_failure = False

        record = InspectionRecord(
            tenant_id=tenant_id,
            inspection_number=insp_num,
            plan_id=payload.plan_id,
            item_id=payload.item_id,
            source_document_type=payload.source_document_type,
            source_document_id=payload.source_document_id,
            inspection_date=payload.inspection_date,
            inspector_id=user_id,
            inspected_quantity=payload.inspected_quantity,
            passed_quantity=payload.passed_quantity,
            rejected_quantity=payload.rejected_quantity,
            status=InspectionStatus.PASS.value,
            remarks=payload.remarks
        )
        db.add(record)
        await db.flush()

        for res_data in payload.results:
            param = params_map.get(res_data.parameter_id)
            is_conforming = True

            if param:
                if param.test_type == TestType.NUMERIC_RANGE.value:
                    if res_data.measured_numeric_value is not None:
                        if param.min_value is not None and res_data.measured_numeric_value < param.min_value:
                            is_conforming = False
                        if param.max_value is not None and res_data.measured_numeric_value > param.max_value:
                            is_conforming = False
                elif param.test_type == TestType.PASS_FAIL.value:
                    is_conforming = res_data.pass_fail_result

                if not is_conforming and param.is_critical:
                    has_critical_failure = True

            r_line = InspectionResultLine(
                tenant_id=tenant_id,
                inspection_record_id=record.id,
                parameter_id=res_data.parameter_id,
                measured_numeric_value=res_data.measured_numeric_value,
                pass_fail_result=res_data.pass_fail_result,
                is_conforming=is_conforming,
                remarks=res_data.remarks
            )
            db.add(r_line)

        if has_critical_failure or pass_ratio < plan.pass_threshold_percentage:
            record.status = InspectionStatus.FAIL.value
        else:
            record.status = InspectionStatus.PASS.value

        await db.commit()
        await db.refresh(record)
        return record

    @classmethod
    async def list_inspections(cls, db: AsyncSession, tenant_id: str) -> List[InspectionRecord]:
        query = (
            select(InspectionRecord)
            .where(InspectionRecord.tenant_id == tenant_id, InspectionRecord.is_deleted == False)
            .options(selectinload(InspectionRecord.results))
            .order_by(InspectionRecord.inspection_date.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
