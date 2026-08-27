"""
NexERP Accounts Payable Payment Run & Batch Disbursement Engine.
Groups approved bills, updates outstanding balances, and generates GL bank disbursement journals.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.accounts_payable.models import VendorBill, PaymentRun, PaymentRunItem, Vendor
from backend.src.modules.accounts_payable.schemas import PaymentRunCreate
from backend.src.modules.accounts_payable.enums import BillStatus, PaymentRunStatus
from backend.src.modules.financials.models import Account, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate


class PaymentRunService:
    """
    Manages payment runs and cash disbursements to vendors.
    """

    @classmethod
    async def generate_run_number(cls, db: AsyncSession, tenant_id: str, run_date: date) -> str:
        year_str = str(run_date.year)
        prefix = f"PAY-{year_str}-"
        query = (
            select(PaymentRun)
            .where(
                PaymentRun.tenant_id == tenant_id,
                PaymentRun.run_number.like(f"{prefix}%")
            )
            .order_by(PaymentRun.run_number.desc())
            .limit(1)
        )
        result = await db.execute(query)
        latest = result.scalar_one_or_none()
        seq = int(latest.run_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def execute_payment_run(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: PaymentRunCreate,
        user_id: str
    ) -> PaymentRun:
        """
        Execute payment run: reduce bill balances, mark paid bills, and post bank disbursement GL entry.
        """
        bank_acc_res = await db.execute(select(Account).where(Account.id == payload.bank_account_id, Account.tenant_id == tenant_id))
        bank_account = bank_acc_res.scalar_one_or_none()
        if not bank_account:
            raise EntityNotFoundError("Bank account not found.")

        # Validate bills
        bill_ids = [it.bill_id for it in payload.items]
        bill_res = await db.execute(
            select(VendorBill)
            .where(VendorBill.id.in_(bill_ids), VendorBill.tenant_id == tenant_id)
            .options(selectinload(VendorBill.vendor))
        )
        bills_map = {b.id: b for b in bill_res.scalars().all()}

        total_run_amount = Decimal("0.0")
        gl_lines = []

        # Find open period
        p_res = await db.execute(select(FiscalPeriod).where(FiscalPeriod.tenant_id == tenant_id, FiscalPeriod.is_locked == False).limit(1))
        period = p_res.scalar_one_or_none()
        if not period:
            raise BusinessRuleViolationError("No open fiscal period available.")

        run_num = await cls.generate_run_number(db, tenant_id, payload.run_date)

        payment_run = PaymentRun(
            tenant_id=tenant_id,
            run_number=run_num,
            run_date=payload.run_date,
            bank_account_id=payload.bank_account_id,
            payment_method=payload.payment_method.value,
            total_amount=Decimal("0.0"),
            status=PaymentRunStatus.POSTED.value,
            notes=payload.notes
        )
        db.add(payment_run)
        await db.flush()

        for it in payload.items:
            bill = bills_map.get(it.bill_id)
            if not bill:
                raise EntityNotFoundError(f"Bill ID '{it.bill_id}' not found.")

            if it.payment_amount > bill.balance_due:
                raise BusinessRuleViolationError(
                    f"Payment amount (${it.payment_amount}) exceeds remaining balance due (${bill.balance_due}) on Bill {bill.bill_number}."
                )

            # Update bill paid amount and balance
            bill.paid_amount = bill.paid_amount + it.payment_amount
            bill.balance_due = bill.balance_due - it.payment_amount

            if bill.balance_due <= Decimal("0.0001"):
                bill.status = BillStatus.PAID.value
            else:
                bill.status = BillStatus.PARTIALLY_PAID.value

            total_run_amount += it.payment_amount

            # Debit AP liability
            ap_acc_id = bill.vendor.ap_account_id
            if not ap_acc_id:
                # Default AP
                ap_def = (await db.execute(select(Account).where(Account.tenant_id == tenant_id, Account.classification == "ACCOUNTS_PAYABLE"))).scalar_one()
                ap_acc_id = ap_def.id

            gl_lines.append(
                JournalEntryLineCreate(
                    account_id=ap_acc_id,
                    debit=it.payment_amount,
                    credit=Decimal("0.0"),
                    description=f"Payment for Bill {bill.bill_number} (Run: {run_num})",
                    partner_type="VENDOR",
                    partner_id=bill.vendor_id
                )
            )

            p_item = PaymentRunItem(
                tenant_id=tenant_id,
                payment_run_id=payment_run.id,
                bill_id=bill.id,
                payment_amount=it.payment_amount,
                early_discount_captured=it.early_discount_captured
            )
            db.add(p_item)

        payment_run.total_amount = total_run_amount

        # Credit Bank Asset for total disbursed
        gl_lines.append(
            JournalEntryLineCreate(
                account_id=payload.bank_account_id,
                debit=Decimal("0.0"),
                credit=total_run_amount,
                description=f"Vendor Batch Payment Run {run_num}"
            )
        )

        # Create & post GL disbursement voucher
        jv_payload = JournalEntryCreate(
            entry_date=payload.run_date,
            period_id=period.id,
            currency="USD",
            exchange_rate=Decimal("1.0"),
            reference=run_num,
            narration=f"Disbursement Payment Run {run_num}",
            source_document_type="PaymentRun",
            source_document_id=payment_run.id,
            lines=gl_lines
        )
        jv = await GeneralLedgerService.create_journal_entry(db, tenant_id, jv_payload, user_id)
        posted_jv = await GeneralLedgerService.post_journal_entry(db, tenant_id, jv.id, user_id)

        payment_run.journal_entry_id = posted_jv.id

        await db.commit()
        await db.refresh(payment_run)
        return payment_run
