"""
NexERP Customer Volume Rebates & Trade Promotion Engine.
Calculates:
- Tiered Annual Spend Rebate Accruals
- Retrospective Customer Rebate Settlement Credit Memos
- General Ledger Contra-Revenue Accounting Accruals.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class CustomerRebatesService:
    """
    Volume Rebates & Trade Promotion Settlement Service.
    """

    # Default Tiered Volume Rebate Agreement Structure
    REBATE_TIERS = [
        (Decimal("50000.00"), Decimal("2.0")),   # $50k - $100k: 2% rebate
        (Decimal("100000.00"), Decimal("4.0")),  # $100k - $250k: 4% rebate
        (Decimal("250000.00"), Decimal("6.0")),  # $250k+: 6% rebate
    ]

    @classmethod
    def calculate_earned_rebate(
        cls,
        customer_id: str,
        customer_name: str,
        annual_qualifying_spend_usd: Decimal,
        rebate_agreement_tiers: Optional[List[tuple]] = None
    ) -> Dict:
        """
        Compute eligible volume rebate percentage and payout credit amount.
        """
        tiers = rebate_agreement_tiers or cls.REBATE_TIERS

        applicable_rebate_pct = Decimal("0.0")
        for threshold, pct in sorted(tiers, key=lambda x: x[0]):
            if annual_qualifying_spend_usd >= threshold:
                applicable_rebate_pct = pct

        rebate_amount = (annual_qualifying_spend_usd * (applicable_rebate_pct / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "annual_qualifying_spend_usd": float(annual_qualifying_spend_usd),
            "earned_rebate_percent": float(applicable_rebate_pct),
            "rebate_credit_memo_amount": float(rebate_amount),
            "is_rebate_eligible": applicable_rebate_pct > Decimal("0.0"),
            "gl_accounting_entry": {
                "debit_account": "Customer Rebates Contra-Revenue (P&L)",
                "credit_account": "Customer Rebates Payable / Accrual",
                "amount": float(rebate_amount)
            } if rebate_amount > Decimal("0.0") else None
        }
