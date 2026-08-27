"""
NexERP General Ledger Posting & Balance Invariant Engine.
Enforces double-entry ledger equality, fiscal period locking, running balance calculations,
and immutable reversal mechanics.
"""

from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import (
    UnbalancedJournalEntryError,
    AccountingPeriodClosedError,
    EntityNotFoundError,
    BusinessRuleViolationError
)
from backend.src.core.events import publish_domain_event, DomainEvent, EVENT_JOURNAL_POSTED
from backend.src.modules.financials.models import (
    Account,
    FiscalPeriod,
    JournalEntry,
    JournalEntryLine
)
from backend.src.modules.financials.schemas import JournalEntryCreate
from backend.src.modules.financials.enums import JournalStatus, AccountType


class GeneralLedgerService:
    """
    Core Double-Entry General Ledger Service.
    """

    @classmethod
    async def generate_voucher_number(cls, db: AsyncSession, tenant_id: str, entry_date: date) -> str:
        """Generate sequential journal voucher number (e.g. JV-2026-00001)."""
        year_str = str(entry_date.year)
        prefix = f"JV-{year_str}-"
        
        query = (
            select(JournalEntry)
            .where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.voucher_number.like(f"{prefix}%")
            )
            .order_by(JournalEntry.voucher_number.desc())
            .limit(1)
        )
        result = await db.execute(query)
        latest = result.scalar_one_or_none()
        
        if latest:
            last_seq = int(latest.voucher_number.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
            
        return f"{prefix}{new_seq:05d}"

    @classmethod
    async def create_journal_entry(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: JournalEntryCreate,
        user_id: Optional[str] = None
    ) -> JournalEntry:
        """
        Validate balanced debits/credits, verify open fiscal period, and save journal entry draft.
        """
        # Verify Fiscal Period
        period_query = select(FiscalPeriod).where(
            FiscalPeriod.id == payload.period_id,
            FiscalPeriod.tenant_id == tenant_id
        )
        p_res = await db.execute(period_query)
        period = p_res.scalar_one_or_none()

        if not period:
            raise EntityNotFoundError("Fiscal period not found.")

        if period.is_locked:
            raise AccountingPeriodClosedError(f"Fiscal period '{period.name}' is closed and locked.")

        # Compute total debits and credits
        total_debit = Decimal("0.0")
        total_credit = Decimal("0.0")

        for line in payload.lines:
            total_debit += line.debit
            total_credit += line.credit

        # Enforce strict balance rule
        tolerance = Decimal("0.0001")
        if abs(total_debit - total_credit) > tolerance:
            raise UnbalancedJournalEntryError(
                message=f"Journal voucher is unbalanced: Total Debits (${total_debit}) != Total Credits (${total_credit}).",
                details={"total_debit": float(total_debit), "total_credit": float(total_credit)}
            )

        if total_debit <= Decimal("0.0"):
            raise BusinessRuleViolationError("Journal entry total amount must be greater than zero.")

        # Validate accounts exist and are not header accounts
        account_ids = [line.account_id for line in payload.lines]
        acc_query = select(Account).where(
            Account.id.in_(account_ids),
            Account.tenant_id == tenant_id,
            Account.is_deleted == False
        )
        acc_res = await db.execute(acc_query)
        accounts_map = {acc.id: acc for acc in acc_res.scalars().all()}

        for line in payload.lines:
            acc = accounts_map.get(line.account_id)
            if not acc:
                raise EntityNotFoundError(f"Account with ID '{line.account_id}' was not found.")
            if acc.is_header_only:
                raise BusinessRuleViolationError(
                    f"Account '{acc.code} - {acc.name}' is a header summary group and cannot receive direct postings."
                )

        # Validate fiscal period
        p_res = await db.execute(
            select(FiscalPeriod).where(
                FiscalPeriod.id == payload.period_id,
                FiscalPeriod.tenant_id == tenant_id
            )
        )
        period = p_res.scalar_one_or_none()
        if not period:
            raise EntityNotFoundError("Fiscal period not found.")
        if period.is_locked:
            raise AccountingPeriodClosedError(f"Fiscal period '{period.name}' is closed and locked.")

        voucher_num = await cls.generate_voucher_number(db, tenant_id, payload.entry_date)

        journal = JournalEntry(
            tenant_id=tenant_id,
            voucher_number=voucher_num,
            entry_date=payload.entry_date,
            period_id=payload.period_id,
            currency=payload.currency,
            exchange_rate=payload.exchange_rate,
            status=JournalStatus.DRAFT.value,
            reference=payload.reference,
            narration=payload.narration,
            source_document_type=payload.source_document_type,
            source_document_id=payload.source_document_id,
            total_debit=total_debit,
            total_credit=total_credit,
            created_by_id=user_id
        )
        db.add(journal)
        await db.flush()

        # Insert Lines
        for idx, line in enumerate(payload.lines, start=1):
            jl = JournalEntryLine(
                tenant_id=tenant_id,
                journal_entry_id=journal.id,
                account_id=line.account_id,
                line_number=idx,
                debit=line.debit,
                credit=line.credit,
                debit_currency=getattr(line, "debit_currency", None) if getattr(line, "debit_currency", None) is not None else (line.debit * payload.exchange_rate),
                credit_currency=getattr(line, "credit_currency", None) if getattr(line, "credit_currency", None) is not None else (line.credit * payload.exchange_rate),
                description=line.description,
                partner_type=line.partner_type,
                partner_id=line.partner_id,
                cost_center_id=line.cost_center_id,
                project_id=line.project_id
            )
            db.add(jl)

        await db.commit()
        await db.refresh(journal)
        return journal

    @classmethod
    async def post_journal_entry(
        cls,
        db: AsyncSession,
        tenant_id: str,
        journal_id: str,
        user_id: str
    ) -> JournalEntry:
        """
        Post a draft journal entry to the general ledger, updating account running balances.
        Once posted, entries cannot be modified—only reversed.
        """
        query = (
            select(JournalEntry)
            .where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.is_deleted == False
            )
            .options(
                selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account),
                selectinload(JournalEntry.period)
            )
        )
        result = await db.execute(query)
        journal = result.scalar_one_or_none()

        if not journal:
            raise EntityNotFoundError("Journal voucher not found.")

        if journal.status == JournalStatus.POSTED.value:
            raise BusinessRuleViolationError("Journal entry is already posted.")

        if journal.period.is_locked:
            raise AccountingPeriodClosedError(f"Fiscal period '{journal.period.name}' is closed and locked.")

        # Update Account Balances
        for line in journal.lines:
            acc = line.account
            current_bal = Decimal(str(acc.current_balance or 0.0))
            # Debit increases Asset & Expense, decreases Liability, Equity, Revenue
            if acc.account_type in [AccountType.ASSET.value, AccountType.EXPENSE.value]:
                acc.current_balance = current_bal + (line.debit - line.credit)
            else:
                acc.current_balance = current_bal + (line.credit - line.debit)

        journal.status = JournalStatus.POSTED.value
        journal.posting_date = date.today()
        journal.posted_at = datetime.now(timezone.utc)
        journal.posted_by_id = user_id

        await db.commit()
        await db.refresh(journal)

        # Dispatch async domain event
        await publish_domain_event(DomainEvent(
            event_name=EVENT_JOURNAL_POSTED,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload={"journal_id": journal.id, "voucher_number": journal.voucher_number, "total_debit": float(journal.total_debit)}
        ))

        return journal

    @classmethod
    async def reverse_journal_entry(
        cls,
        db: AsyncSession,
        tenant_id: str,
        journal_id: str,
        reversal_date: date,
        reason: str,
        user_id: str
    ) -> JournalEntry:
        """
        Create and post an exact inverse reversal voucher to void a previously posted journal entry.
        """
        query = (
            select(JournalEntry)
            .where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.is_deleted == False
            )
            .options(
                selectinload(JournalEntry.lines),
                selectinload(JournalEntry.period)
            )
        )
        result = await db.execute(query)
        original = result.scalar_one_or_none()

        if not original:
            raise EntityNotFoundError("Original journal voucher not found.")

        if original.status != JournalStatus.POSTED.value:
            raise BusinessRuleViolationError("Only posted journal entries can be reversed.")

        if original.reversed_entry_id:
            raise BusinessRuleViolationError("Journal entry has already been reversed.")

        # Invert debits and credits
        reversed_lines = []
        for line in original.lines:
            reversed_lines.append(
                JournalEntryLine(
                    tenant_id=tenant_id,
                    account_id=line.account_id,
                    line_number=line.line_number,
                    debit=line.credit,
                    credit=line.debit,
                    debit_currency=line.credit_currency,
                    credit_currency=line.debit_currency,
                    description=f"Reversal of {original.voucher_number}: {line.description or ''}".strip(),
                    partner_type=line.partner_type,
                    partner_id=line.partner_id,
                    cost_center_id=line.cost_center_id,
                    project_id=line.project_id
                )
            )

        rev_voucher_num = await cls.generate_voucher_number(db, tenant_id, reversal_date)

        reversal_entry = JournalEntry(
            tenant_id=tenant_id,
            voucher_number=rev_voucher_num,
            entry_date=reversal_date,
            posting_date=reversal_date,
            period_id=original.period_id,
            currency=original.currency,
            exchange_rate=original.exchange_rate,
            status=JournalStatus.POSTED.value,
            reference=f"REV:{original.voucher_number}",
            narration=f"Reversal of {original.voucher_number}. Reason: {reason}",
            source_document_type="JournalReversal",
            source_document_id=original.id,
            total_debit=original.total_credit,
            total_credit=original.total_debit,
            posted_at=datetime.now(timezone.utc),
            posted_by_id=user_id,
            created_by_id=user_id,
            lines=reversed_lines
        )
        db.add(reversal_entry)
        await db.flush()

        # Update account balances for reversal
        for line in reversed_lines:
            acc_res = await db.execute(select(Account).where(Account.id == line.account_id))
            acc = acc_res.scalar_one()
            current_bal = Decimal(str(acc.current_balance or 0.0))
            if acc.account_type in [AccountType.ASSET.value, AccountType.EXPENSE.value]:
                acc.current_balance = current_bal + (line.debit - line.credit)
            else:
                acc.current_balance = current_bal + (line.credit - line.debit)

        # Mark original as reversed
        original.status = JournalStatus.REVERSED.value
        original.reversed_entry_id = reversal_entry.id

        await db.commit()
        await db.refresh(reversal_entry)
        return reversal_entry
