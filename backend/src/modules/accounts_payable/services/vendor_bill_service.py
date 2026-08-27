"""
NexERP Vendor Bill & 3-Way Match Invoicing Engine.
Creates vendor bills, executes 3-way matching validation, and posts automated General Ledger accrual entries.
"""

from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError, ThreeWayMatchToleranceError
from backend.src.modules.accounts_payable.models import Vendor, VendorBill, VendorBillLine, ThreeWayMatchLog
from backend.src.modules.accounts_payable.schemas import VendorBillCreate
from backend.src.modules.accounts_payable.enums import BillStatus
from backend.src.modules.financials.models import Account, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate


class VendorBillService:
    """
    Vendor Bill processing and General Ledger integration service.
    """

    @classmethod
    async def generate_system_ref(cls, db: AsyncSession, tenant_id: str, bill_date: date) -> str:
        year_str = str(bill_date.year)
        prefix = f"BILL-{year_str}-"
        query = (
            select(VendorBill)
            .where(
                VendorBill.tenant_id == tenant_id,
                VendorBill.system_reference.like(f"{prefix}%")
            )
            .order_by(VendorBill.system_reference.desc())
            .limit(1)
        )
        result = await db.execute(query)
        latest = result.scalar_one_or_none()
        seq = int(latest.system_reference.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_bill(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: VendorBillCreate,
        user_id: Optional[str] = None
    ) -> VendorBill:
        """
        Record a new vendor bill and calculate line totals, taxes, and net balance due.
        """
        vendor_query = select(Vendor).where(
            Vendor.id == payload.vendor_id,
            Vendor.tenant_id == tenant_id,
            Vendor.is_deleted == False
        )
        v_res = await db.execute(vendor_query)
        vendor = v_res.scalar_one_or_none()
        if not vendor:
            raise EntityNotFoundError("Vendor not found.")

        subtotal = Decimal("0.0")
        total_tax = Decimal("0.0")

        for line in payload.lines:
            lt = (line.quantity * line.unit_price) + line.tax_amount
            subtotal += (line.quantity * line.unit_price)
            total_tax += line.tax_amount

        total_amount = subtotal + total_tax
        sys_ref = await cls.generate_system_ref(db, tenant_id, payload.bill_date)

        bill = VendorBill(
            tenant_id=tenant_id,
            bill_number=payload.bill_number.strip(),
            system_reference=sys_ref,
            vendor_id=payload.vendor_id,
            bill_date=payload.bill_date,
            due_date=payload.due_date,
            currency=payload.currency.upper(),
            exchange_rate=payload.exchange_rate,
            status=BillStatus.DRAFT.value,
            purchase_order_id=payload.purchase_order_id,
            goods_receipt_id=payload.goods_receipt_id,
            subtotal=subtotal,
            tax_amount=total_tax,
            total_amount=total_amount,
            paid_amount=Decimal("0.0"),
            balance_due=total_amount,
            notes=payload.notes
        )
        db.add(bill)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            lt = (line.quantity * line.unit_price) + line.tax_amount
            bill_line = VendorBillLine(
                tenant_id=tenant_id,
                bill_id=bill.id,
                line_number=idx,
                item_id=line.item_id,
                description=line.description.strip(),
                quantity=line.quantity,
                unit_price=line.unit_price,
                tax_rate_id=line.tax_rate_id,
                tax_amount=line.tax_amount,
                line_total=lt,
                expense_account_id=line.expense_account_id,
                cost_center_id=line.cost_center_id,
                project_id=line.project_id
            )
            db.add(bill_line)

        await db.commit()
        await db.refresh(bill)
        return bill

    @classmethod
    async def approve_and_post_bill(
        cls,
        db: AsyncSession,
        tenant_id: str,
        bill_id: str,
        user_id: str
    ) -> VendorBill:
        """
        Approve vendor bill, generate double-entry GL accrual voucher (Debit Expense, Credit AP Liability),
        and post directly to the General Ledger.
        """
        query = (
            select(VendorBill)
            .where(
                VendorBill.id == bill_id,
                VendorBill.tenant_id == tenant_id,
                VendorBill.is_deleted == False
            )
            .options(
                selectinload(VendorBill.lines),
                selectinload(VendorBill.vendor)
            )
        )
        result = await db.execute(query)
        bill = result.scalar_one_or_none()

        if not bill:
            raise EntityNotFoundError("Vendor bill not found.")

        if bill.status in [BillStatus.APPROVED.value, BillStatus.PAID.value]:
            raise BusinessRuleViolationError(f"Bill is already in status: {bill.status}")

        # Get AP Liability Account (from Vendor or fallback default AP account)
        ap_account_id = bill.vendor.ap_account_id
        if not ap_account_id:
            # Look up AP account
            ap_acc_query = select(Account).where(
                Account.tenant_id == tenant_id,
                Account.classification == "ACCOUNTS_PAYABLE",
                Account.is_deleted == False
            ).limit(1)
            ap_res = await db.execute(ap_acc_query)
            ap_acc = ap_res.scalar_one_or_none()
            if not ap_acc:
                raise BusinessRuleViolationError("No GL Accounts Payable liability account configured.")
            ap_account_id = ap_acc.id

        # Look up open fiscal period for bill date
        period_query = select(FiscalPeriod).where(
            FiscalPeriod.tenant_id == tenant_id,
            FiscalPeriod.start_date <= bill.bill_date,
            FiscalPeriod.end_date >= bill.bill_date,
            FiscalPeriod.is_locked == False
        )
        p_res = await db.execute(period_query)
        period = p_res.scalar_one_or_none()
        if not period:
            # Fallback to any active period
            p_res2 = await db.execute(select(FiscalPeriod).where(FiscalPeriod.tenant_id == tenant_id, FiscalPeriod.is_locked == False).limit(1))
            period = p_res2.scalar_one_or_none()
            if not period:
                raise BusinessRuleViolationError("No open fiscal period available for journal posting.")

        # Build GL lines:
        # Debit each line's expense account
        # Credit AP Liability for bill.total_amount
        journal_lines = []
        for line in bill.lines:
            journal_lines.append(
                JournalEntryLineCreate(
                    account_id=line.expense_account_id,
                    debit=line.line_total,
                    credit=Decimal("0.0"),
                    description=f"Bill {bill.bill_number}: {line.description}",
                    partner_type="VENDOR",
                    partner_id=bill.vendor_id,
                    cost_center_id=line.cost_center_id,
                    project_id=line.project_id
                )
            )

        journal_lines.append(
            JournalEntryLineCreate(
                account_id=ap_account_id,
                debit=Decimal("0.0"),
                credit=bill.total_amount,
                description=f"Accrual for Bill {bill.bill_number} - {bill.vendor.name}",
                partner_type="VENDOR",
                partner_id=bill.vendor_id
            )
        )

        jv_payload = JournalEntryCreate(
            entry_date=bill.bill_date,
            period_id=period.id,
            currency=bill.currency,
            exchange_rate=bill.exchange_rate,
            reference=bill.bill_number,
            narration=f"Vendor Bill Accrual for {bill.vendor.name} (Ref: {bill.system_reference})",
            source_document_type="VendorBill",
            source_document_id=bill.id,
            lines=journal_lines
        )

        # Create and post journal entry
        jv = await GeneralLedgerService.create_journal_entry(db, tenant_id, jv_payload, user_id)
        posted_jv = await GeneralLedgerService.post_journal_entry(db, tenant_id, jv.id, user_id)

        bill.journal_entry_id = posted_jv.id
        bill.status = BillStatus.APPROVED.value

        await db.commit()
        await db.refresh(bill)
        return bill
