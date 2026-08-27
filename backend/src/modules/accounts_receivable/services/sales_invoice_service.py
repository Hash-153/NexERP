"""
NexERP Sales Invoice & General Ledger Integration Service.
Computes invoice totals, validates customer credit limits, and posts automated GL revenue vouchers.
"""

from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import (
    EntityNotFoundError,
    BusinessRuleViolationError,
    CreditLimitExceededError
)
from backend.src.core.events import publish_domain_event, DomainEvent, EVENT_INVOICE_CREATED
from backend.src.modules.accounts_receivable.models import Customer, SalesInvoice, SalesInvoiceLine
from backend.src.modules.accounts_receivable.schemas import SalesInvoiceCreate
from backend.src.modules.accounts_receivable.enums import InvoiceStatus
from backend.src.modules.financials.models import Account, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate


class SalesInvoiceService:
    """
    Sales Invoice lifecycle and General Ledger revenue recognition service.
    """

    @classmethod
    async def generate_invoice_number(cls, db: AsyncSession, tenant_id: str, invoice_date: date) -> str:
        year_str = str(invoice_date.year)
        prefix = f"INV-{year_str}-"
        query = (
            select(SalesInvoice)
            .where(
                SalesInvoice.tenant_id == tenant_id,
                SalesInvoice.invoice_number.like(f"{prefix}%")
            )
            .order_by(SalesInvoice.invoice_number.desc())
            .limit(1)
        )
        result = await db.execute(query)
        latest = result.scalar_one_or_none()
        seq = int(latest.invoice_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_invoice(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: SalesInvoiceCreate,
        user_id: Optional[str] = None
    ) -> SalesInvoice:
        """
        Record sales invoice, check credit limits, and persist draft invoice with lines.
        """
        cust_query = select(Customer).where(
            Customer.id == payload.customer_id,
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False
        )
        c_res = await db.execute(cust_query)
        customer = c_res.scalar_one_or_none()

        if not customer:
            raise EntityNotFoundError("Customer account not found.")

        if customer.credit_hold:
            raise CreditLimitExceededError("Customer account is on credit hold. Cannot issue new sales invoice.")

        subtotal = Decimal("0.0")
        total_discount = Decimal("0.0")
        total_tax = Decimal("0.0")

        for line in payload.lines:
            gross = line.quantity * line.unit_price
            disc = gross * (line.discount_percent / Decimal("100.0"))
            net_line = gross - disc
            subtotal += net_line
            total_discount += disc
            total_tax += line.tax_amount

        total_amount = subtotal + total_tax

        # Check credit limit
        if (customer.current_balance + total_amount) > customer.credit_limit:
            raise CreditLimitExceededError(
                f"Invoice total (${total_amount}) causes outstanding balance (${customer.current_balance + total_amount}) to exceed approved credit limit (${customer.credit_limit})."
            )

        inv_num = await cls.generate_invoice_number(db, tenant_id, payload.invoice_date)

        invoice = SalesInvoice(
            tenant_id=tenant_id,
            invoice_number=inv_num,
            customer_id=payload.customer_id,
            invoice_date=payload.invoice_date,
            due_date=payload.due_date,
            currency=payload.currency.upper(),
            exchange_rate=payload.exchange_rate,
            status=InvoiceStatus.DRAFT.value,
            sales_order_id=payload.sales_order_id,
            fulfillment_delivery_id=payload.fulfillment_delivery_id,
            subtotal=subtotal,
            discount_amount=total_discount,
            tax_amount=total_tax,
            total_amount=total_amount,
            paid_amount=Decimal("0.0"),
            balance_due=total_amount,
            notes=payload.notes
        )
        db.add(invoice)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            gross = line.quantity * line.unit_price
            disc = gross * (line.discount_percent / Decimal("100.0"))
            net_line = gross - disc + line.tax_amount

            inv_line = SalesInvoiceLine(
                tenant_id=tenant_id,
                invoice_id=invoice.id,
                line_number=idx,
                item_id=line.item_id,
                description=line.description.strip(),
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                tax_rate_id=line.tax_rate_id,
                tax_amount=line.tax_amount,
                line_total=net_line,
                revenue_account_id=line.revenue_account_id,
                cost_center_id=line.cost_center_id,
                project_id=line.project_id
            )
            db.add(inv_line)

        await db.commit()
        await db.refresh(invoice)
        return invoice

    @classmethod
    async def post_sales_invoice(
        cls,
        db: AsyncSession,
        tenant_id: str,
        invoice_id: str,
        user_id: str
    ) -> SalesInvoice:
        """
        Post sales invoice to General Ledger:
        - Debit Accounts Receivable Asset for total_amount
        - Credit Sales Revenue Account for net product total
        - Credit Tax Liability Account for tax_amount
        - Update customer outstanding receivable balance.
        """
        query = (
            select(SalesInvoice)
            .where(
                SalesInvoice.id == invoice_id,
                SalesInvoice.tenant_id == tenant_id,
                SalesInvoice.is_deleted == False
            )
            .options(
                selectinload(SalesInvoice.lines),
                selectinload(SalesInvoice.customer)
            )
        )
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise EntityNotFoundError("Sales invoice not found.")

        if invoice.status != InvoiceStatus.DRAFT.value:
            raise BusinessRuleViolationError(f"Invoice is already in status: {invoice.status}")

        # Get Customer AR Account
        ar_account_id = invoice.customer.ar_account_id
        if not ar_account_id:
            ar_acc_query = select(Account).where(
                Account.tenant_id == tenant_id,
                Account.classification == "ACCOUNTS_RECEIVABLE",
                Account.is_deleted == False
            ).limit(1)
            ar_res = await db.execute(ar_acc_query)
            ar_acc = ar_res.scalar_one_or_none()
            if not ar_acc:
                raise BusinessRuleViolationError("No GL Accounts Receivable asset account configured.")
            ar_account_id = ar_acc.id

        # Open fiscal period
        period_query = select(FiscalPeriod).where(
            FiscalPeriod.tenant_id == tenant_id,
            FiscalPeriod.start_date <= invoice.invoice_date,
            FiscalPeriod.end_date >= invoice.invoice_date,
            FiscalPeriod.is_locked == False
        )
        p_res = await db.execute(period_query)
        period = p_res.scalar_one_or_none()
        if not period:
            p_res2 = await db.execute(select(FiscalPeriod).where(FiscalPeriod.tenant_id == tenant_id, FiscalPeriod.is_locked == False).limit(1))
            period = p_res2.scalar_one_or_none()
            if not period:
                raise BusinessRuleViolationError("No open fiscal period available.")

        # Build GL lines
        journal_lines = [
            # Debit Accounts Receivable
            JournalEntryLineCreate(
                account_id=ar_account_id,
                debit=invoice.total_amount,
                credit=Decimal("0.0"),
                description=f"Receivable for Invoice {invoice.invoice_number} - {invoice.customer.name}",
                partner_type="CUSTOMER",
                partner_id=invoice.customer_id
            )
        ]

        # Credit Revenue accounts per line
        for line in invoice.lines:
            journal_lines.append(
                JournalEntryLineCreate(
                    account_id=line.revenue_account_id,
                    debit=Decimal("0.0"),
                    credit=line.line_total - line.tax_amount,
                    description=f"Sales Revenue: {line.description}",
                    partner_type="CUSTOMER",
                    partner_id=invoice.customer_id,
                    cost_center_id=line.cost_center_id,
                    project_id=line.project_id
                )
            )

        # Credit Tax Liability if tax > 0
        if invoice.tax_amount > Decimal("0.0"):
            # Lookup Tax Liability Account
            tax_acc_query = select(Account).where(
                Account.tenant_id == tenant_id,
                Account.classification == "TAX_PAYABLE",
                Account.is_deleted == False
            ).limit(1)
            tax_res = await db.execute(tax_acc_query)
            tax_acc = tax_res.scalar_one_or_none()
            if tax_acc:
                journal_lines.append(
                    JournalEntryLineCreate(
                        account_id=tax_acc.id,
                        debit=Decimal("0.0"),
                        credit=invoice.tax_amount,
                        description=f"Sales Tax Payable on Invoice {invoice.invoice_number}"
                    )
                )

        jv_payload = JournalEntryCreate(
            entry_date=invoice.invoice_date,
            period_id=period.id,
            currency=invoice.currency,
            exchange_rate=invoice.exchange_rate,
            reference=invoice.invoice_number,
            narration=f"Sales Invoice Revenue Posting for {invoice.customer.name}",
            source_document_type="SalesInvoice",
            source_document_id=invoice.id,
            lines=journal_lines
        )

        jv = await GeneralLedgerService.create_journal_entry(db, tenant_id, jv_payload, user_id)
        posted_jv = await GeneralLedgerService.post_journal_entry(db, tenant_id, jv.id, user_id)

        # Update invoice & customer balance
        invoice.journal_entry_id = posted_jv.id
        invoice.status = InvoiceStatus.POSTED.value
        invoice.customer.current_balance = invoice.customer.current_balance + invoice.total_amount

        await db.commit()
        await db.refresh(invoice)

        # Dispatch event
        await publish_domain_event(DomainEvent(
            event_name=EVENT_INVOICE_CREATED,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload={"invoice_id": invoice.id, "invoice_number": invoice.invoice_number, "total_amount": float(invoice.total_amount)}
        ))

        return invoice
