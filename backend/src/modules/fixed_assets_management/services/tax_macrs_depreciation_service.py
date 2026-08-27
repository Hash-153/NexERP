"""
US Federal Tax MACRS GDS & ADS Depreciation Calculation Service (IRS Publication 946).
"""
from decimal import Decimal
from typing import Dict, Any, List

class TaxMACRSDepreciationService:
    # MACRS 5-Year Property Half-Year Convention percentages
    MACRS_5_YEAR_RATES = [
        Decimal("0.2000"),
        Decimal("0.3200"),
        Decimal("0.1920"),
        Decimal("0.1152"),
        Decimal("0.1152"),
        Decimal("0.0576"),
    ]

    # MACRS 7-Year Property Half-Year Convention percentages
    MACRS_7_YEAR_RATES = [
        Decimal("0.1429"),
        Decimal("0.2449"),
        Decimal("0.1749"),
        Decimal("0.1249"),
        Decimal("0.0893"),
        Decimal("0.0892"),
        Decimal("0.0893"),
        Decimal("0.0446"),
    ]

    @classmethod
    def calculate_macrs_schedule(
        cls,
        cost_basis: Decimal,
        recovery_period_years: int = 5,
        section_179_deduction: Decimal = Decimal("0.0"),
        bonus_depreciation_pct: Decimal = Decimal("0.60")  # 60% bonus depreciation for 2024-2026
    ) -> List[Dict[str, Any]]:
        depreciable_base = cost_basis - section_179_deduction
        bonus_amount = (depreciable_base * bonus_depreciation_pct).quantize(Decimal("0.01"))
        macrs_base = depreciable_base - bonus_amount

        rates = cls.MACRS_5_YEAR_RATES if recovery_period_years == 5 else cls.MACRS_7_YEAR_RATES
        schedule = []
        accumulated = section_179_deduction + bonus_amount

        for year_idx, rate in enumerate(rates, start=1):
            annual_depr = (macrs_base * rate).quantize(Decimal("0.01"))
            if year_idx == 1:
                total_year_1 = annual_depr + bonus_amount + section_179_deduction
                accumulated_year = total_year_1
                carrying_val = cost_basis - accumulated_year
                schedule.append({
                    "tax_year": year_idx,
                    "macrs_rate": float(rate),
                    "base_depreciation": float(annual_depr),
                    "bonus_depreciation": float(bonus_amount),
                    "section_179": float(section_179_deduction),
                    "total_tax_depreciation": float(total_year_1),
                    "ending_tax_basis": float(carrying_val)
                })
            else:
                accumulated += annual_depr
                carrying_val = max(Decimal("0.0"), cost_basis - accumulated)
                schedule.append({
                    "tax_year": year_idx,
                    "macrs_rate": float(rate),
                    "base_depreciation": float(annual_depr),
                    "bonus_depreciation": 0.0,
                    "section_179": 0.0,
                    "total_tax_depreciation": float(annual_depr),
                    "ending_tax_basis": float(carrying_val)
                })

        return schedule
