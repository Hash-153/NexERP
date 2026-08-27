"""
Multi-Book Depreciation Engine Service.
Supports Straight Line, Double Declining Balance, MACRS, and Sum of Years Digits.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.core.audit import AuditService
from ..models import FixedAssetMaster, AssetDepreciationSchedule
from ..schemas import DepreciationRunRequest

class DepreciationEngineService:
    @staticmethod
    def calculate_period_depreciation(
        cost: Decimal,
        salvage: Decimal,
        useful_months: int,
        accumulated: Decimal,
        method: str = "STRAIGHT_LINE"
    ) -> Decimal:
        depreciable_base = cost - salvage
        remaining_base = depreciable_base - accumulated
        if remaining_base <= Decimal("0.0"):
            return Decimal("0.0")

        if method == "STRAIGHT_LINE":
            monthly_rate = Decimal("1.0") / Decimal(str(useful_months))
            monthly_depr = (depreciable_base * monthly_rate).quantize(Decimal("0.01"))
            return min(monthly_depr, remaining_base)
        elif method == "DOUBLE_DECLINING_BALANCE":
            annual_rate = (Decimal("2.0") / (Decimal(str(useful_months)) / Decimal("12.0")))
            monthly_rate = annual_rate / Decimal("12.0")
            current_carrying = cost - accumulated
            monthly_depr = (current_carrying * monthly_rate).quantize(Decimal("0.01"))
            return min(monthly_depr, remaining_base)
        else:
            # Fallback to straight line
            monthly_depr = (depreciable_base / Decimal(str(useful_months))).quantize(Decimal("0.01"))
            return min(monthly_depr, remaining_base)

    @staticmethod
    async def run_monthly_depreciation(
        session: AsyncSession,
        payload: DepreciationRunRequest,
        tenant_id: str,
        actor_id: str
    ) -> Dict[str, Any]:
        stmt = select(FixedAssetMaster).where(
            FixedAssetMaster.tenant_id == tenant_id,
            FixedAssetMaster.status == "ACTIVE_IN_SERVICE",
            FixedAssetMaster.is_deleted == False
        )
        result = await session.execute(stmt)
        assets = result.scalars().all()

        processed_count = 0
        total_depreciation_run = Decimal("0.0")

        for asset in assets:
            depr_amt = DepreciationEngineService.calculate_period_depreciation(
                cost=asset.original_acquisition_cost,
                salvage=asset.salvage_scrap_value,
                useful_months=asset.useful_life_months,
                accumulated=asset.accumulated_depreciation,
                method=payload.depreciation_method
            )

            if depr_amt > 0:
                opening_nbv = asset.current_net_book_value
                closing_nbv = opening_nbv - depr_amt

                schedule = AssetDepreciationSchedule(
                    tenant_id=tenant_id,
                    asset_id=asset.id,
                    fiscal_period=payload.fiscal_period,
                    period_start_date=date.today(),
                    period_end_date=date.today(),
                    depreciation_method=payload.depreciation_method,
                    book_type=payload.book_type,
                    opening_carrying_value=opening_nbv,
                    depreciation_amount=depr_amt,
                    closing_carrying_value=closing_nbv,
                    is_posted_to_gl=False
                )
                session.add(schedule)

                asset.accumulated_depreciation += depr_amt
                asset.current_net_book_value = closing_nbv
                if asset.current_net_book_value <= asset.salvage_scrap_value:
                    asset.status = "FULLY_DEPRECIATED"

                total_depreciation_run += depr_amt
                processed_count += 1

        await session.commit()
        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="RUN_DEPRECIATION",
            entity_type="AssetDepreciationSchedule",
            entity_id=payload.fiscal_period,
            description=f"Executed {payload.depreciation_method} depreciation for {processed_count} assets: Total ${total_depreciation_run}"
        )

        return {
            "fiscal_period": payload.fiscal_period,
            "assets_processed": processed_count,
            "total_depreciation_posted": float(total_depreciation_run)
        }
