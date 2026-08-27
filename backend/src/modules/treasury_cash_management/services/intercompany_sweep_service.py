"""
Automated Intercompany Cash Sweeping & Notional Pooling Service.
"""
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import BusinessRuleViolationError
from backend.src.core.audit import AuditService
from ..models import TreasuryBankAccount, TreasuryTransaction

class IntercompanySweepService:
    @staticmethod
    async def execute_zero_balance_sweeps(
        session: AsyncSession,
        tenant_id: str,
        actor_id: str
    ) -> List[Dict[str, Any]]:
        # Find target header account
        stmt_target = select(TreasuryBankAccount).where(
            TreasuryBankAccount.tenant_id == tenant_id,
            TreasuryBankAccount.is_sweep_target == True,
            TreasuryBankAccount.is_deleted == False
        )
        result_target = await session.execute(stmt_target)
        target_account = result_target.scalar_one_or_none()
        if not target_account:
            return []

        # Find all source participant accounts
        stmt_sources = select(TreasuryBankAccount).where(
            TreasuryBankAccount.tenant_id == tenant_id,
            TreasuryBankAccount.is_sweep_source == True,
            TreasuryBankAccount.id != target_account.id,
            TreasuryBankAccount.is_deleted == False
        )
        result_sources = await session.execute(stmt_sources)
        sources = result_sources.scalars().all()

        sweep_logs = []
        for src in sources:
            surplus = src.available_cleared_balance - src.target_balance
            if abs(surplus) > Decimal("100.00"):
                # Sweep excess funds to target or fund shortfall from target
                src.available_cleared_balance -= surplus
                target_account.available_cleared_balance += surplus
                
                sweep_logs.append({
                    "source_account": src.account_number,
                    "target_account": target_account.account_number,
                    "swept_amount": float(surplus),
                    "source_final_balance": float(src.available_cleared_balance),
                    "direction": "SURPLUS_SWEEP_UP" if surplus > 0 else "DEFICIT_FUNDING_DOWN"
                })

        await session.commit()
        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="EXECUTE_CASH_SWEEP",
            entity_type="TreasuryBankAccount",
            entity_id=target_account.id,
            description=f"Executed zero-balance cash sweep across {len(sweep_logs)} sub-accounts."
        )
        return sweep_logs
