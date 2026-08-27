"""
NexERP Global Trade Management (GTM) & Harmonized System (HS) Customs Tariff Engine.
Calculates import customs duty tariffs, Ad Valorem rates, Specific Duty rates,
and Harbor Maintenance / Merchandise Processing Fees (MPF/HMF).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional


class CustomsTariffService:
    """
    Harmonized Tariff Schedule (HTS) & Customs Duty Calculation Service.
    """

    # Common HTS Tariffs: (HTS Code, General Duty %, Merchandise Category)
    HTS_SCHEDULE = {
        "8471.30.01": {"duty_rate": Decimal("0.0"), "category": "Portable Automatic Data Processing Machines / Laptops"},
        "8501.10.40": {"duty_rate": Decimal("0.044"), "category": "Electric Motors under 18.65W (4.4% Ad Valorem)"},
        "8482.10.50": {"duty_rate": Decimal("0.090"), "category": "Ball Bearings (9.0% Ad Valorem)"},
        "7318.15.20": {"duty_rate": Decimal("0.085"), "category": "Bolts and Screws of Iron or Steel (8.5%)"},
        "8473.30.1180": {"duty_rate": Decimal("0.0"), "category": "Printed Circuit Assemblies / Electronics (0%)"},
    }

    @classmethod
    def calculate_customs_duties(
        cls,
        hts_code: str,
        customs_declared_value_usd: Decimal,
        origin_country_code: str,
        destination_country_code: str = "USA",
        apply_section_301_tariff: bool = False
    ) -> Dict:
        """
        Compute import duty liability, standard MPF (Merchandise Processing Fee), and trade tariffs.
        """
        hts_clean = hts_code.strip()
        tariff_entry = cls.HTS_SCHEDULE.get(hts_clean, {"duty_rate": Decimal("0.035"), "category": "General Industrial Goods (3.5% Default)"})

        base_ad_valorem_rate = tariff_entry["duty_rate"]
        base_duty_amount = (customs_declared_value_usd * base_ad_valorem_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Section 301 / Trade Remedy Surcharge (e.g. 25% for specific country origin lanes)
        section_301_rate = Decimal("0.25") if (apply_section_301_tariff or origin_country_code.upper() == "CN") else Decimal("0.0")
        section_301_duty = (customs_declared_value_usd * section_301_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # US Customs Merchandise Processing Fee (MPF): 0.3464% (Min $31.67, Max $614.35)
        mpf_raw = customs_declared_value_usd * Decimal("0.003464")
        mpf_fee = max(Decimal("31.67"), min(Decimal("614.35"), mpf_raw)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_customs_obligation = base_duty_amount + section_301_duty + mpf_fee
        effective_tariff_rate = ((total_customs_obligation / customs_declared_value_usd) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if customs_declared_value_usd > Decimal("0.0") else Decimal("0.0")

        return {
            "hts_code": hts_clean,
            "category_description": tariff_entry["category"],
            "customs_declared_value_usd": float(customs_declared_value_usd),
            "origin_country": origin_country_code.upper(),
            "destination_country": destination_country_code.upper(),
            "base_duty_rate_percent": float(base_ad_valorem_rate * Decimal("100.0")),
            "base_duty_amount_usd": float(base_duty_amount),
            "section_301_tariff_amount_usd": float(section_301_duty),
            "merchandise_processing_fee_mpf": float(mpf_fee),
            "total_customs_duty_payable": float(total_customs_obligation),
            "effective_tariff_rate_percent": float(effective_tariff_rate)
        }
