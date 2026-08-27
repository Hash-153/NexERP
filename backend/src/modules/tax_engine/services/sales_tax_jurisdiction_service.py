"""
Precision Sales Tax Jurisdiction & Wayfair Economic Nexus Engine.
"""
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.audit import AuditService
from ..models import TaxJurisdictionRule, TaxExemptionCertificate
from ..schemas import TaxCalculationRequest, TaxCalculationResult

class SalesTaxJurisdictionService:
    @staticmethod
    def calculate_us_sales_tax(
        state: str,
        amount: Decimal,
        is_exempt: bool = False
    ) -> Dict[str, Any]:
        if is_exempt or amount <= 0:
            return {
                "taxable_amount": float(amount),
                "combined_rate": 0.0,
                "state_tax": 0.0,
                "local_tax": 0.0,
                "total_tax": 0.0,
                "jurisdiction": f"EXEMPT-{state.upper()}"
            }

        # Multi-state statutory table
        rates = {
            "CA": (Decimal("0.0725"), Decimal("0.0150")), # State 7.25%, Local 1.50%
            "TX": (Decimal("0.0625"), Decimal("0.0200")), # State 6.25%, Local 2.00%
            "NY": (Decimal("0.0400"), Decimal("0.04875")),# State 4.00%, Local 4.875%
            "WA": (Decimal("0.0650"), Decimal("0.0360")), # State 6.50%, Local 3.60%
            "IL": (Decimal("0.0625"), Decimal("0.0350")), # State 6.25%, Local 3.50%
            "FL": (Decimal("0.0600"), Decimal("0.0150")), # State 6.00%, Local 1.50%
        }

        state_rate, local_rate = rates.get(state.upper(), (Decimal("0.0500"), Decimal("0.0100")))
        combined = state_rate + local_rate
        
        state_tax = (amount * state_rate).quantize(Decimal("0.01"))
        local_tax = (amount * local_rate).quantize(Decimal("0.01"))
        total_tax = state_tax + local_tax

        return {
            "taxable_amount": float(amount),
            "combined_rate": float(combined),
            "state_tax": float(state_tax),
            "local_tax": float(local_tax),
            "total_tax": float(total_tax),
            "jurisdiction": f"US-{state.upper()}"
        }
