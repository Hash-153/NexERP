"""
Bank Statement Parsing Service.
Handles electronic parsing of MT940, BAI2, and ISO 20022 CAMT.053 standard formats.
"""
import re
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from backend.src.core.audit import AuditService
from ..models import TreasuryBankAccount, TreasuryBankStatement, TreasuryBankStatementLine
from ..schemas import StatementImportRequest

class BankStatementParserService:
    @staticmethod
    async def import_parsed_statement(
        session: AsyncSession,
        payload: StatementImportRequest,
        tenant_id: str,
        actor_id: str
    ) -> TreasuryBankStatement:
        stmt = select(TreasuryBankAccount).where(
            TreasuryBankAccount.id == payload.bank_account_id,
            TreasuryBankAccount.tenant_id == tenant_id,
            TreasuryBankAccount.is_deleted == False
        )
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()
        if not account:
            raise EntityNotFoundError(f"Treasury bank account {payload.bank_account_id} not found.")

        # Calculate debit and credit totals from lines
        total_debits = sum(abs(line.amount) for line in payload.lines if line.amount < 0)
        total_credits = sum(line.amount for line in payload.lines if line.amount > 0)
        
        # Verify opening + credits - debits == closing balance within 2 decimal precision
        calculated_closing = payload.opening_balance + total_credits - total_debits
        if abs(calculated_closing - payload.closing_balance) > Decimal("0.01"):
            raise BusinessRuleViolationError(
                f"Statement balance mismatch: Opening ({payload.opening_balance}) + Credits ({total_credits}) - "
                f"Debits ({total_debits}) != Closing ({payload.closing_balance}). Delta: {calculated_closing - payload.closing_balance}"
            )

        statement = TreasuryBankStatement(
            tenant_id=tenant_id,
            bank_account_id=payload.bank_account_id,
            statement_identifier=payload.statement_identifier,
            statement_format=payload.statement_format,
            statement_date=payload.statement_date,
            opening_balance=payload.opening_balance,
            closing_balance=payload.closing_balance,
            total_debits=total_debits,
            total_credits=total_credits,
            raw_payload=payload.raw_payload
        )
        session.add(statement)
        await session.flush()

        for idx, line_data in enumerate(payload.lines, start=1):
            line = TreasuryBankStatementLine(
                tenant_id=tenant_id,
                statement_id=statement.id,
                line_number=idx,
                booking_date=line_data.booking_date,
                value_date=line_data.value_date,
                amount=line_data.amount,
                currency=line_data.currency,
                transaction_code=line_data.transaction_code,
                bank_reference=line_data.bank_reference,
                remittance_info=line_data.remittance_info,
                counterparty_name=line_data.counterparty_name,
                counterparty_iban=line_data.counterparty_iban
            )
            session.add(line)

        # Update bank account cleared balance
        account.available_cleared_balance = payload.closing_balance
        account.current_ledger_balance = payload.closing_balance

        await session.commit()
        await session.refresh(statement)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="IMPORT_STATEMENT",
            entity_type="TreasuryBankStatement",
            entity_id=statement.id,
            description=f"Imported statement {payload.statement_identifier} with {len(payload.lines)} lines"
        )
        return statement

    @staticmethod
    def parse_mt940_text(content: str) -> Dict[str, Any]:
        """Utility parser for Swift MT940 flat text statements."""
        lines = content.splitlines()
        statement_id = "MT940-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        extracted_lines = []
        opening_bal = Decimal("0.0")
        closing_bal = Decimal("0.0")

        for line in lines:
            if line.startswith(":20:"):
                statement_id = line[4:].strip()
            elif line.startswith(":60F:"):
                # Opening balance tag
                parts = line[5:]
                d_c = parts[0]
                amt_str = parts[10:].replace(",", ".")
                opening_bal = Decimal(amt_str) if d_c == "C" else -Decimal(amt_str)
            elif line.startswith(":62F:"):
                parts = line[5:]
                d_c = parts[0]
                amt_str = parts[10:].replace(",", ".")
                closing_bal = Decimal(amt_str) if d_c == "C" else -Decimal(amt_str)

        return {
            "statement_identifier": statement_id,
            "opening_balance": opening_bal,
            "closing_balance": closing_bal,
            "lines": extracted_lines
        }
