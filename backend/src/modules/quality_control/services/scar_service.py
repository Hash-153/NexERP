"""
NexERP Supplier Corrective Action Request (SCAR) Lifecycle Engine.
Manages:
- Supplier Non-Conformance ticketing from receiving inspection or shop floor defects
- SCAR Issuance with mandatory 8D response deadline (e.g. 14 days)
- Containment verification, root cause approval, and supplier rating impact penalty.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional


class SCARManagementService:
    """
    Supplier Corrective Action Request (SCAR) Quality Service.
    """

    @classmethod
    def issue_scar_notice(
        cls,
        scar_number: str,
        vendor_id: str,
        vendor_name: str,
        item_sku: str,
        grn_number: str,
        defect_description: str,
        defect_quantity: int,
        severity_level: str = "MAJOR",
        response_window_days: int = 14
    ) -> Dict:
        """
        Create and dispatch a formal SCAR notice to supplier.
        """
        issue_date = date.today()
        deadline_date = issue_date + timedelta(days=response_window_days)

        return {
            "scar_number": scar_number,
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "item_sku": item_sku,
            "associated_grn": grn_number,
            "defect_summary": defect_description,
            "defective_parts_count": defect_quantity,
            "severity_level": severity_level.upper(),
            "issued_date": issue_date.isoformat(),
            "response_deadline_date": deadline_date.isoformat(),
            "status": "PENDING_SUPPLIER_8D",
            "scorecard_penalty_points": 15 if severity_level.upper() == "CRITICAL" else 5,
            "required_deliverables": [
                "Immediate 24hr Containment Confirmation",
                "Root Cause Analysis (5-Whys)",
                "Permanent Corrective Action (PCA) Plan",
                "Preventive Control Plan & FMEA Revision"
            ]
        }
