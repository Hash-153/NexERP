"""
NexERP Fiscal Calendar, Period Closing & Year-End Processing Service.
"""

from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.financials.models import FiscalYear, FiscalPeriod
from backend.src.modules.financials.schemas import FiscalYearCreate


class FiscalPeriodService:
    """
    Manages annual fiscal calendars and hard/soft period closes.
    """

    @classmethod
    async def create_fiscal_year_with_12_periods(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: FiscalYearCreate
    ) -> FiscalYear:
        """
        Initialize a new fiscal year along with 12 standard calendar monthly periods.
        """
        fy = FiscalYear(
            tenant_id=tenant_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_closed=False
        )
        db.add(fy)
        await db.flush()

        # Generate 12 periods
        current_start = payload.start_date
        for p_num in range(1, 13):
            # Estimate month end
            if p_num == 12:
                period_end = payload.end_date
            else:
                # Add roughly 1 month (or exact month arithmetic)
                next_month = current_start.month + 1 if current_start.month < 12 else 1
                next_year = current_start.year if current_start.month < 12 else current_start.year + 1
                next_start = date(next_year, next_month, 1)
                period_end = next_start - timedelta(days=1)

            period = FiscalPeriod(
                tenant_id=tenant_id,
                fiscal_year_id=fy.id,
                period_number=p_num,
                name=f"{fy.name} - Period {p_num:02d}",
                start_date=current_start,
                end_date=period_end,
                is_locked=False,
                is_adjustment_period=False
            )
            db.add(period)
            if p_num < 12:
                current_start = period_end + timedelta(days=1)

        await db.commit()
        
        # Eagerly load periods
        q = select(FiscalYear).where(FiscalYear.id == fy.id).options(selectinload(FiscalYear.periods))
        res = await db.execute(q)
        return res.scalar_one()

    @classmethod
    async def lock_period(cls, db: AsyncSession, tenant_id: str, period_id: str) -> FiscalPeriod:
        """Lock an accounting period to prevent new journal postings."""
        query = select(FiscalPeriod).where(
            FiscalPeriod.id == period_id,
            FiscalPeriod.tenant_id == tenant_id
        )
        result = await db.execute(query)
        period = result.scalar_one_or_none()

        if not period:
            raise EntityNotFoundError("Fiscal period not found.")

        period.is_locked = True
        await db.commit()
        await db.refresh(period)
        return period

    @classmethod
    async def unlock_period(cls, db: AsyncSession, tenant_id: str, period_id: str) -> FiscalPeriod:
        """Reopen a previously locked accounting period (Auditor / CFO authorization)."""
        query = select(FiscalPeriod).where(
            FiscalPeriod.id == period_id,
            FiscalPeriod.tenant_id == tenant_id
        )
        result = await db.execute(query)
        period = result.scalar_one_or_none()

        if not period:
            raise EntityNotFoundError("Fiscal period not found.")

        period.is_locked = False
        await db.commit()
        await db.refresh(period)
        return period

    @classmethod
    async def list_fiscal_years(cls, db: AsyncSession, tenant_id: str) -> List[FiscalYear]:
        query = (
            select(FiscalYear)
            .where(FiscalYear.tenant_id == tenant_id, FiscalYear.is_deleted == False)
            .options(selectinload(FiscalYear.periods))
            .order_by(FiscalYear.start_date.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())
