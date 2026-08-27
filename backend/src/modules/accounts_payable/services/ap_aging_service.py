"""
NexERP Accounts Payable Aging Report Engine.
Calculates outstanding vendor balances across current, 1-30, 31-60, 61-90, and 90+ days aging buckets.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.modules.accounts_payable.models import Vendor, VendorBill
from backend.src.modules.accounts_payable.enums import BillStatus
from backend.src.modules.accounts_payable.schemas import APAgingReportResponse, APAgingBucket


class APAgingService:
    """
    Computes Accounts Payable aging breakdown for cash management forecasting.
    """

    @classmethod
    async def generate_aging_report(
        cls,
        db: AsyncSession,
        tenant_id: str,
        as_of_date: date
    ) -> APAgingReportResponse:
        """
        Generate vendor aging matrix based on bill due dates vs as_of_date.
        """
        # Query all unpaid/partially paid approved bills
        query = (
            select(VendorBill)
            .where(
                VendorBill.tenant_id == tenant_id,
                VendorBill.status.in_([BillStatus.APPROVED.value, BillStatus.PARTIALLY_PAID.value]),
                VendorBill.balance_due > Decimal("0.0"),
                VendorBill.is_deleted == False
            )
            .options(selectinload(VendorBill.vendor))
        )
        result = await db.execute(query)
        bills = result.scalars().all()

        vendor_data: Dict[str, Dict] = {}

        total_curr = Decimal("0.0")
        total_1_30 = Decimal("0.0")
        total_31_60 = Decimal("0.0")
        total_61_90 = Decimal("0.0")
        total_90_plus = Decimal("0.0")
        grand_total = Decimal("0.0")

        for bill in bills:
            v = bill.vendor
            if v.id not in vendor_data:
                vendor_data[v.id] = {
                    "vendor_id": v.id,
                    "vendor_name": v.name,
                    "vendor_code": v.code,
                    "current": Decimal("0.0"),
                    "days_1_30": Decimal("0.0"),
                    "days_31_60": Decimal("0.0"),
                    "days_61_90": Decimal("0.0"),
                    "days_90_plus": Decimal("0.0"),
                    "total": Decimal("0.0"),
                }

            days_overdue = (as_of_date - bill.due_date).days
            due = bill.balance_due

            if days_overdue <= 0:
                vendor_data[v.id]["current"] += due
                total_curr += due
            elif 1 <= days_overdue <= 30:
                vendor_data[v.id]["days_1_30"] += due
                total_1_30 += due
            elif 31 <= days_overdue <= 60:
                vendor_data[v.id]["days_31_60"] += due
                total_31_60 += due
            elif 61 <= days_overdue <= 90:
                vendor_data[v.id]["days_61_90"] += due
                total_61_90 += due
            else:
                vendor_data[v.id]["days_90_plus"] += due
                total_90_plus += due

            vendor_data[v.id]["total"] += due
            grand_total += due

        buckets = [
            APAgingBucket(
                vendor_id=d["vendor_id"],
                vendor_name=d["vendor_name"],
                vendor_code=d["vendor_code"],
                current=d["current"],
                days_1_30=d["days_1_30"],
                days_31_60=d["days_31_60"],
                days_61_90=d["days_61_90"],
                days_90_plus=d["days_90_plus"],
                total_outstanding=d["total"]
            )
            for d in vendor_data.values()
        ]

        return APAgingReportResponse(
            as_of_date=as_of_date,
            vendors=buckets,
            total_current=total_curr,
            total_1_30=total_1_30,
            total_31_60=total_31_60,
            total_61_90=total_61_90,
            total_90_plus=total_90_plus,
            grand_total=grand_total
        )
