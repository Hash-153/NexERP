"""
NexERP Vendor Performance Evaluation & Scorecard Service.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.procurement.models import VendorEvaluation
from backend.src.modules.procurement.schemas import VendorEvaluationCreate
from backend.src.modules.accounts_payable.models import Vendor


class VendorEvaluationService:
    """
    Vendor scorecard calculation and audit manager.
    """

    @classmethod
    async def evaluate_vendor(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: VendorEvaluationCreate,
        user_id: Optional[str] = None
    ) -> VendorEvaluation:
        v_res = await db.execute(select(Vendor).where(Vendor.id == payload.vendor_id, Vendor.tenant_id == tenant_id))
        vendor = v_res.scalar_one_or_none()
        if not vendor:
            raise EntityNotFoundError("Vendor not found.")

        # Weighted calculation: 40% Quality, 40% Delivery, 20% Pricing
        overall = (payload.quality_score * Decimal("0.40")) + \
                  (payload.on_time_delivery_score * Decimal("0.40")) + \
                  (payload.pricing_score * Decimal("0.20"))

        eval_rec = VendorEvaluation(
            tenant_id=tenant_id,
            vendor_id=payload.vendor_id,
            evaluation_date=payload.evaluation_date,
            quality_score=payload.quality_score,
            on_time_delivery_score=payload.on_time_delivery_score,
            pricing_score=payload.pricing_score,
            overall_rating=overall.quantize(Decimal("0.01")),
            evaluator_id=user_id,
            remarks=payload.remarks
        )
        db.add(eval_rec)
        await db.commit()
        await db.refresh(eval_rec)
        return eval_rec

    @classmethod
    async def list_evaluations(cls, db: AsyncSession, tenant_id: str, vendor_id: Optional[str] = None) -> List[VendorEvaluation]:
        query = select(VendorEvaluation).where(VendorEvaluation.tenant_id == tenant_id)
        if vendor_id:
            query = query.where(VendorEvaluation.vendor_id == vendor_id)
        query = query.order_by(VendorEvaluation.evaluation_date.desc())
        res = await db.execute(query)
        return list(res.scalars().all())
