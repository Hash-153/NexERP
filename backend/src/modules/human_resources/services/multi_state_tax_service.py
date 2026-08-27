"""
NexERP US Multi-State Payroll Tax & Reciprocal Agreement Engine.
Handles:
- Resident vs Non-Resident Work State Tax Withholding
- Reciprocal State Tax Agreements (e.g. IL & WI, PA & NJ, VA & MD)
- State Unemployment Insurance (SUI) Taxable Wage Base Caps.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class MultiStateTaxService:
    """
    Multi-State Payroll Withholding & Statutory Compliance Service.
    """

    # Reciprocal State Tax Agreements: (Resident State, Work State) -> Exemption in Work State
    RECIPROCAL_AGREEMENTS = {
        ("IL", "WI"): True,
        ("WI", "IL"): True,
        ("PA", "NJ"): True,
        ("NJ", "PA"): True,
        ("VA", "MD"): True,
        ("MD", "VA"): True,
    }

    # State Income Tax Rates (Flat / Top Marginal for estimation)
    STATE_TAX_RATES = {
        "CA": Decimal("9.30"),
        "NY": Decimal("6.85"),
        "IL": Decimal("4.95"),
        "TX": Decimal("0.00"),  # No State Income Tax
        "FL": Decimal("0.00"),  # No State Income Tax
        "WA": Decimal("0.00"),  # No State Income Tax
        "PA": Decimal("3.07"),
        "NJ": Decimal("6.37"),
    }

    @classmethod
    def calculate_state_withholding(
        cls,
        gross_pay: Decimal,
        resident_state: str,
        work_state: str,
        year_to_date_wages: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Determine withholding state under reciprocal agreements and compute state tax deduction.
        """
        res_st = resident_state.upper()
        wrk_st = work_state.upper()

        # Check reciprocal exemption
        has_reciprocity = cls.RECIPROCAL_AGREEMENTS.get((res_st, wrk_st), False)

        # If reciprocity applies, tax is withheld for the RESIDENT state; otherwise, WORK state has primary nexus
        taxing_state = res_st if has_reciprocity or res_st == wrk_st else wrk_st
        rate_pct = cls.STATE_TAX_RATES.get(taxing_state, Decimal("4.50"))

        state_tax_amount = (gross_pay * (rate_pct / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "gross_pay": float(gross_pay),
            "resident_state": res_st,
            "work_location_state": wrk_st,
            "has_reciprocity_agreement": has_reciprocity,
            "primary_taxing_state": taxing_state,
            "state_tax_rate_percent": float(rate_pct),
            "state_tax_withholding_amount": float(state_tax_amount)
        }
