"""
Multi-State Sales Tax & International VAT Nexus Engine.
"""
from decimal import Decimal
from typing import Dict, Any, List

class SalesTaxCalculatorService:
    # State standard statutory tax rates
    STATE_TAX_RATES = {
        "CA": Decimal("0.0725"),
        "TX": Decimal("0.0625"),
        "NY": Decimal("0.0400"),
        "WA": Decimal("0.0650"),
        "IL": Decimal("0.0625"),
        "FL": Decimal("0.0600"),
        "PA": Decimal("0.0600"),
        "OH": Decimal("0.0575"),
        "DE": Decimal("0.0000"),  # No sales tax
        "OR": Decimal("0.0000"),  # No sales tax
    }

    VAT_RATES = {
        "GB": Decimal("0.20"),
        "DE": Decimal("0.19"),
        "FR": Decimal("0.20"),
        "NL": Decimal("0.21"),
        "IE": Decimal("0.23"),
    }

    @classmethod
    def calculate_line_taxes(
        cls,
        line_amount: Decimal,
        is_taxable: bool,
        destination_state: str,
        destination_country: str = "US",
        is_exempt: bool = False
    ) -> Dict[str, Any]:
        if not is_taxable or is_exempt or line_amount <= 0:
            return {
                "taxable_amount": float(line_amount),
                "tax_rate": 0.0,
                "calculated_tax": 0.0,
                "jurisdiction": "EXEMPT"
            }

        if destination_country == "US":
            rate = cls.STATE_TAX_RATES.get(destination_state.upper(), Decimal("0.0500"))
            jurisdiction = f"US-{destination_state.upper()}"
        else:
            rate = cls.VAT_RATES.get(destination_country.upper(), Decimal("0.2000"))
            jurisdiction = f"VAT-{destination_country.upper()}"

        tax_amt = (line_amount * rate).quantize(Decimal("0.01"))
        return {
            "taxable_amount": float(line_amount),
            "tax_rate": float(rate),
            "calculated_tax": float(tax_amt),
            "jurisdiction": jurisdiction
        }
