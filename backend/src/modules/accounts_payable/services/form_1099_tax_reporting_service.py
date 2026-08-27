"""
US IRS Form 1099-NEC & 1099-MISC Electronic Reporting Subsystem.
Aggregates vendor non-employee compensation across calendar tax years with threshold alerts ($600).
"""
from decimal import Decimal
from typing import Dict, Any, List

class Form1099TaxReportingService:
    IRS_THRESHOLD = Decimal("600.00")

    @classmethod
    def evaluate_vendor_1099_eligibility(
        cls,
        vendor_tax_id: str,
        vendor_legal_name: str,
        entity_type: str, # INDIVIDUAL_SOLE_PROP, LLC_DISREGARDED, CORPORATION
        annual_payments: Decimal
    ) -> Dict[str, Any]:
        is_reportable = False
        form_type = "NONE"

        if entity_type in ("INDIVIDUAL_SOLE_PROP", "LLC_DISREGARDED", "PARTNERSHIP"):
            if annual_payments >= cls.IRS_THRESHOLD:
                is_reportable = True
                form_type = "FORM_1099_NEC"

        return {
            "vendor_legal_name": vendor_legal_name,
            "vendor_tax_id_masked": f"XX-XXX{vendor_tax_id[-4:]}" if len(vendor_tax_id) >= 4 else "XX-XXXXXXX",
            "entity_type": entity_type,
            "total_annual_payments": float(annual_payments),
            "is_1099_reportable": is_reportable,
            "form_type": form_type,
            "box_1_nonemployee_compensation": float(annual_payments) if is_reportable else 0.0
        }
