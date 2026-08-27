"""
NexERP Accounts Receivable Dunning & Credit Control Engine.
Monitors overdue invoices, elevates dunning stages, assesses interest penalties, and triggers credit holds.
"""

from datetime import date
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.modules.accounts_receivable.models import Customer, SalesInvoice, DunningNotice
from backend.src.modules.accounts_receivable.enums import InvoiceStatus, DunningLevel


class DunningService:
    """
    Automated credit risk monitoring and dunning cycle processor.
    """

    DEFAULT_ANNUAL_PENALTY_RATE = Decimal("0.12")  # 12% per annum late interest

    @classmethod
    async def process_dunning_cycle(
        cls,
        db: AsyncSession,
        tenant_id: str,
        as_of_date: date
    ) -> List[DunningNotice]:
        """
        Scan all overdue customer accounts, advance dunning level, calculate interest,
        and place credit holds on accounts exceeding 60+ days delinquent.
        """
        query = (
            select(Customer)
            .where(Customer.tenant_id == tenant_id, Customer.is_deleted == False)
            .options(
                selectinload(Customer.invoices)
            )
        )
        result = await db.execute(query)
        customers = result.scalars().all()

        generated_notices = []

        for cust in customers:
            overdue_sum = Decimal("0.0")
            max_days_overdue = 0

            for inv in cust.invoices:
                if inv.status in [InvoiceStatus.POSTED.value, InvoiceStatus.PARTIALLY_PAID.value] and inv.balance_due > 0:
                    days_over = (as_of_date - inv.due_date).days
                    if days_over > 0:
                        overdue_sum += inv.balance_due
                        max_days_overdue = max(max_days_overdue, days_over)

            if overdue_sum > Decimal("0.0"):
                # Determine Dunning Stage
                if max_days_overdue > 60:
                    stage = DunningLevel.LEVEL_3_DEMAND.value
                    cust.credit_hold = True  # Automatically freeze credit
                elif max_days_overdue > 30:
                    stage = DunningLevel.LEVEL_2_WARNING.value
                else:
                    stage = DunningLevel.LEVEL_1_REMINDER.value

                # Interest calculation: (overdue * rate * days) / 365
                interest = (overdue_sum * cls.DEFAULT_ANNUAL_PENALTY_RATE * Decimal(max_days_overdue)) / Decimal("365.0")
                interest = interest.quantize(Decimal("0.01"))

                notice = DunningNotice(
                    tenant_id=tenant_id,
                    customer_id=cust.id,
                    dunning_level=stage,
                    notice_date=as_of_date,
                    overdue_balance=overdue_sum,
                    interest_charged=interest,
                    status="ISSUED"
                )
                db.add(notice)
                generated_notices.append(notice)

        await db.commit()
        return generated_notices
