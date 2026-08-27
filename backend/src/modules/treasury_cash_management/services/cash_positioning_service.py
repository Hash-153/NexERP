"""
Real-time Cash Positioning & Multi-currency Aggregation Engine.
"""
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import TreasuryBankAccount, TreasuryTransaction

class CashPositioningService:
    @staticmethod
    async def get_intraday_cash_position(
        session: AsyncSession,
        tenant_id: str,
        base_currency: str = "USD"
    ) -> Dict[str, Any]:
        stmt = select(TreasuryBankAccount).where(
            TreasuryBankAccount.tenant_id == tenant_id,
            TreasuryBankAccount.is_deleted == False,
            TreasuryBankAccount.is_active == True
        )
        result = await session.execute(stmt)
        accounts = result.scalars().all()

        total_liquid_base = Decimal("0.0")
        currency_breakdown: Dict[str, Decimal] = {}
        account_summaries = []

        for acc in accounts:
            curr = acc.currency
            bal = acc.available_cleared_balance
            currency_breakdown[curr] = currency_breakdown.get(curr, Decimal("0.0")) + bal
            # In production, FX rates would be fetched from the FX engine
            approx_base_equiv = bal  # placeholder 1:1 if same currency
            total_liquid_base += approx_base_equiv

            account_summaries.append({
                "account_id": acc.id,
                "bank_name": acc.bank_name,
                "account_number": acc.account_number,
                "currency": acc.currency,
                "cleared_balance": float(acc.available_cleared_balance),
                "ledger_balance": float(acc.current_ledger_balance),
                "overdraft_limit": float(acc.overdraft_limit),
                "target_balance": float(acc.target_balance),
                "is_sweep_target": acc.is_sweep_target
            })

        return {
            "tenant_id": tenant_id,
            "base_currency": base_currency,
            "total_liquidity_base_equivalent": float(total_liquid_base),
            "currency_breakdown": {k: float(v) for k, v in currency_breakdown.items()},
            "account_count": len(accounts),
            "accounts": account_summaries
        }
