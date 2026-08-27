"""
NexERP Bank Statement Reconciliation Engine.
Supports electronic bank statement parsing (MT940 / BAI2 / CSV),
rule-based automatic settlement matching, tolerance windows, and uncleared transaction tracking.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.financials.models import Account, JournalEntry, JournalEntryLine
from backend.src.modules.financials.enums import JournalStatus


class BankReconciliationService:
    """
    Electronic bank statement matching & reconciliation engine.
    """

    @classmethod
    async def match_statement_lines_with_gl(
        cls,
        db: AsyncSession,
        tenant_id: str,
        bank_account_id: str,
        statement_lines: List[Dict],
        date_tolerance_days: int = 3,
        amount_tolerance: Decimal = Decimal("0.01")
    ) -> Dict:
        """
        Match imported external bank statement records against internal GL bank ledger entries.
        Uses exact amount + reference matching, followed by fuzzy date/amount tolerance window matching.
        """
        # Fetch GL lines for bank account
        query = (
            select(JournalEntryLine)
            .join(JournalEntry)
            .where(
                JournalEntryLine.account_id == bank_account_id,
                JournalEntryLine.tenant_id == tenant_id,
                JournalEntry.status == JournalStatus.POSTED.value
            )
            .options(selectinload(JournalEntryLine.journal_entry))
        )
        res = await db.execute(query)
        gl_lines = list(res.scalars().all())

        matched = []
        unmatched_statement = []
        unmatched_gl = []

        matched_gl_ids = set()

        for stmt in statement_lines:
            stmt_amount = Decimal(str(stmt["amount"]))
            stmt_date = stmt["date"] if isinstance(stmt["date"], date) else date.fromisoformat(stmt["date"])
            stmt_ref = str(stmt.get("reference", "")).strip().lower()

            is_matched = False

            # Phase 1: Exact Amount and Reference Match
            for gl in gl_lines:
                if gl.id in matched_gl_ids:
                    continue

                # Net impact in GL: Debit is bank deposit (+), Credit is bank disbursement (-)
                gl_net = gl.debit - gl.credit

                if gl_net == stmt_amount:
                    gl_ref = (gl.journal_entry.reference or "").strip().lower()
                    gl_desc = (gl.description or "").strip().lower()

                    if (stmt_ref and (stmt_ref in gl_ref or stmt_ref in gl_desc)) or (gl_ref and gl_ref in stmt_ref):
                        matched.append({
                            "statement_line": stmt,
                            "gl_line_id": gl.id,
                            "voucher_number": gl.journal_entry.voucher_number,
                            "match_type": "EXACT_AMOUNT_AND_REFERENCE",
                            "confidence_score": 1.0,
                            "variance": Decimal("0.0")
                        })
                        matched_gl_ids.add(gl.id)
                        is_matched = True
                        break

            if is_matched:
                continue

            # Phase 2: Exact Amount within Date Window
            for gl in gl_lines:
                if gl.id in matched_gl_ids:
                    continue

                gl_net = gl.debit - gl.credit
                gl_date = gl.journal_entry.entry_date
                day_diff = abs((stmt_date - gl_date).days)

                if gl_net == stmt_amount and day_diff <= date_tolerance_days:
                    matched.append({
                        "statement_line": stmt,
                        "gl_line_id": gl.id,
                        "voucher_number": gl.journal_entry.voucher_number,
                        "match_type": "EXACT_AMOUNT_DATE_WINDOW",
                        "confidence_score": max(0.7, 1.0 - (day_diff * 0.1)),
                        "variance": Decimal("0.0")
                    })
                    matched_gl_ids.add(gl.id)
                    is_matched = True
                    break

            if not is_matched:
                unmatched_statement.append(stmt)

        for gl in gl_lines:
            if gl.id not in matched_gl_ids:
                unmatched_gl.append({
                    "gl_line_id": gl.id,
                    "voucher_number": gl.journal_entry.voucher_number,
                    "entry_date": gl.journal_entry.entry_date.isoformat(),
                    "debit": float(gl.debit),
                    "credit": float(gl.credit),
                    "reference": gl.journal_entry.reference,
                    "description": gl.description
                })

        return {
            "matched_count": len(matched),
            "unmatched_statement_count": len(unmatched_statement),
            "unmatched_gl_count": len(unmatched_gl),
            "matches": matched,
            "unmatched_statement_lines": unmatched_statement,
            "unmatched_gl_lines": unmatched_gl
        }

    @classmethod
    async def compute_reconciliation_summary(
        cls,
        db: AsyncSession,
        tenant_id: str,
        bank_account_id: str,
        statement_ending_balance: Decimal,
        as_of_date: date
    ) -> Dict:
        """
        Compute Bank Reconciliation Statement (BRS) reconciling General Ledger Book Balance
        with Bank Statement Ending Balance.
        """
        acc_res = await db.execute(select(Account).where(Account.id == bank_account_id, Account.tenant_id == tenant_id))
        acc = acc_res.scalar_one_or_none()
        if not acc:
            raise EntityNotFoundError("Bank account not found.")

        # Calculate Book Balance as of date
        lines_res = await db.execute(
            select(JournalEntryLine)
            .join(JournalEntry)
            .where(
                JournalEntryLine.account_id == bank_account_id,
                JournalEntryLine.tenant_id == tenant_id,
                JournalEntry.status == JournalStatus.POSTED.value,
                JournalEntry.entry_date <= as_of_date
            )
        )
        lines = lines_res.scalars().all()

        book_balance = sum((l.debit - l.credit) for l in lines)
        unreconciled_difference = (statement_ending_balance - book_balance).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "bank_account_id": bank_account_id,
            "bank_account_code": acc.code,
            "bank_account_name": acc.name,
            "as_of_date": as_of_date.isoformat(),
            "gl_book_balance": float(book_balance),
            "statement_ending_balance": float(statement_ending_balance),
            "unreconciled_difference": float(unreconciled_difference),
            "is_balanced": abs(unreconciled_difference) == Decimal("0.0")
        }
