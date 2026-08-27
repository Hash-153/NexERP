"""
NexERP Customer Payment Receipt & Multi-Invoice Allocation Service.
Records incoming cash/wire collections, settles open invoices, updates customer balances, and posts GL bank receipts.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.core.events import publish_domain_event, DomainEvent, EVENT_PAYMENT_RECEIVED
from backend.src.modules.accounts_receivable.models import (
    Customer,
    SalesInvoice,
    PaymentReceipt,
    ReceiptAllocation
)
from backend.src.modules.accounts_receivable.schemas import PaymentReceiptCreate
from backend.src.modules.accounts_receivable.enums import InvoiceStatus, ReceiptStatus
from backend.src.modules.financials.models import Account, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate


class PaymentReceiptService:
    """
    Manages customer payment collection, invoice settlement allocations, and GL bank postings.
    """

    @classmethod
    async def generate_receipt_number(cls, db: AsyncSession, tenant_id: str, receipt_date: date) -> str:
        year_str = str(receipt_date.year)
        prefix = f"RCT-{year_str}-"
        query = (
            select(PaymentReceipt)
            .where(
                PaymentReceipt.tenant_id == tenant_id,
                PaymentReceipt.receipt_number.like(f"{prefix}%")
            )
            .order_by(PaymentReceipt.receipt_number.desc())
            .limit(1)
        )
        result = await db.execute(query)
        latest = result.scalar_one_or_none()
        seq = int(latest.receipt_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def record_payment_receipt(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: PaymentReceiptCreate,
        user_id: str
    ) -> PaymentReceipt:
        """
        Record customer payment, allocate across open invoices, reduce customer balance,
        and post GL entry: Debit Bank Asset, Credit Accounts Receivable Asset.
        """
        cust_query = select(Customer).where(
            Customer.id == payload.customer_id,
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False
        )
        c_res = await db.execute(cust_query)
        customer = c_res.scalar_one_or_none()
        if not customer:
            raise EntityNotFoundError("Customer not found.")

        bank_acc_res = await db.execute(
            select(Account).where(Account.id == payload.bank_account_id, Account.tenant_id == tenant_id)
        )
        bank_account = bank_acc_res.scalar_one_or_none()
        if not bank_account:
            raise EntityNotFoundError("Bank account not found.")

        # Find open period
        p_res = await db.execute(select(FiscalPeriod).where(FiscalPeriod.tenant_id == tenant_id, FiscalPeriod.is_locked == False).limit(1))
        period = p_res.scalar_one_or_none()
        if not period:
            raise BusinessRuleViolationError("No open fiscal period available.")

        allocated_sum = Decimal("0.0")
        for alloc in payload.allocations:
            allocated_sum += alloc.allocated_amount

        if allocated_sum > payload.total_amount:
            raise BusinessRuleViolationError(
                f"Sum of allocations (${allocated_sum}) exceeds total payment receipt amount (${payload.total_amount})."
            )

        unallocated = payload.total_amount - allocated_sum
        rct_num = await cls.generate_receipt_number(db, tenant_id, payload.receipt_date)

        receipt = PaymentReceipt(
            tenant_id=tenant_id,
            receipt_number=rct_num,
            customer_id=payload.customer_id,
            receipt_date=payload.receipt_date,
            bank_account_id=payload.bank_account_id,
            payment_method=payload.payment_method,
            total_amount=payload.total_amount,
            unallocated_amount=unallocated,
            status=ReceiptStatus.POSTED.value,
            notes=payload.notes
        )
        db.add(receipt)
        await db.flush()

        # Process allocations
        for alloc in payload.allocations:
            inv_query = select(SalesInvoice).where(
                SalesInvoice.id == alloc.invoice_id,
                SalesInvoice.tenant_id == tenant_id
            )
            inv_res = await db.execute(inv_query)
            invoice = inv_res.scalar_one_or_none()
            if not invoice:
                raise EntityNotFoundError(f"Invoice ID '{alloc.invoice_id}' not found.")

            if alloc.allocated_amount > invoice.balance_due:
                raise BusinessRuleViolationError(
                    f"Allocated payment (${alloc.allocated_amount}) exceeds remaining balance due (${invoice.balance_due}) on Invoice {invoice.invoice_number}."
                )

            invoice.paid_amount = invoice.paid_amount + alloc.allocated_amount
            invoice.balance_due = invoice.balance_due - alloc.allocated_amount

            if invoice.balance_due <= Decimal("0.0001"):
                invoice.status = InvoiceStatus.PAID.value
            else:
                invoice.status = InvoiceStatus.PARTIALLY_PAID.value

            rec_alloc = ReceiptAllocation(
                tenant_id=tenant_id,
                receipt_id=receipt.id,
                invoice_id=invoice.id,
                allocated_amount=alloc.allocated_amount,
                early_discount_taken=alloc.early_discount_taken
            )
            db.add(rec_alloc)

        # Update customer running balance
        customer.current_balance = max(Decimal("0.0"), customer.current_balance - payload.total_amount)

        # Build GL lines:
        # Debit Bank Account
        # Credit AR Account
        ar_account_id = customer.ar_account_id
        if not ar_account_id:
            ar_acc_query = select(Account).where(Account.tenant_id == tenant_id, Account.classification == "ACCOUNTS_RECEIVABLE").limit(1)
            ar_acc_res = await db.execute(ar_acc_query)
            ar_account_id = ar_acc_res.scalar_one().id

        gl_lines = [
            JournalEntryLineCreate(
                account_id=payload.bank_account_id,
                debit=payload.total_amount,
                credit=Decimal("0.0"),
                description=f"Customer Collection {rct_num} - {customer.name}",
                partner_type="CUSTOMER",
                partner_id=customer.id
            ),
            JournalEntryLineCreate(
                account_id=ar_account_id,
                debit=Decimal("0.0"),
                credit=payload.total_amount,
                description=f"Payment settlement for {customer.name} (Receipt: {rct_num})",
                partner_type="CUSTOMER",
                partner_id=customer.id
            )
        ]

        jv_payload = JournalEntryCreate(
            entry_date=payload.receipt_date,
            period_id=period.id,
            currency="USD",
            exchange_rate=Decimal("1.0"),
            reference=rct_num,
            narration=f"Customer Payment Receipt {rct_num} from {customer.name}",
            source_document_type="PaymentReceipt",
            source_document_id=receipt.id,
            lines=gl_lines
        )

        jv = await GeneralLedgerService.create_journal_entry(db, tenant_id, jv_payload, user_id)
        posted_jv = await GeneralLedgerService.post_journal_entry(db, tenant_id, jv.id, user_id)

        receipt.journal_entry_id = posted_jv.id

        await db.commit()
        await db.refresh(receipt)

        # Dispatch event
        await publish_domain_event(DomainEvent(
            event_name=EVENT_PAYMENT_RECEIVED,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload={"receipt_id": receipt.id, "receipt_number": receipt.receipt_number, "total_amount": float(receipt.total_amount)}
        ))

        return receipt
