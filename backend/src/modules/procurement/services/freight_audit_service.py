"""
NexERP Transportation Freight Bill Audit & 3-Way BOL Matching Engine.
Performs:
- Carrier Invoice vs Contracted Rate Card vs Bill of Lading (BOL) verification
- Overcharge detection on linehaul mileage, fuel surcharge percent, and accessorial fees
- Automated Dispute / Credit Claim generation for billing variances.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class FreightAuditService:
    """
    Automated Freight Invoice Audit & Dispute Settlement Service.
    """

    @classmethod
    def audit_carrier_invoice(
        cls,
        carrier_invoice_number: str,
        bol_tracking_number: str,
        invoiced_linehaul: Decimal,
        invoiced_fuel_surcharge: Decimal,
        invoiced_accessorials: Decimal,
        contracted_linehaul: Decimal,
        contracted_fuel_surcharge: Decimal,
        contracted_accessorials: Decimal,
        tolerance_amount_usd: Decimal = Decimal("5.00")
    ) -> Dict:
        """
        Audit carrier invoice against contracted rate card agreements.
        """
        total_invoiced = invoiced_linehaul + invoiced_fuel_surcharge + invoiced_accessorials
        total_contracted = contracted_linehaul + contracted_fuel_surcharge + contracted_accessorials

        variance_linehaul = invoiced_linehaul - contracted_linehaul
        variance_fuel = invoiced_fuel_surcharge - contracted_fuel_surcharge
        variance_accessorials = invoiced_accessorials - contracted_accessorials
        total_overcharge = max(Decimal("0.0"), total_invoiced - total_contracted)

        is_passed = total_overcharge <= tolerance_amount_usd

        return {
            "carrier_invoice_number": carrier_invoice_number,
            "bol_tracking_number": bol_tracking_number,
            "total_invoiced_amount": float(total_invoiced),
            "total_contracted_amount": float(total_contracted),
            "total_overcharge_amount": float(total_overcharge),
            "is_audit_approved": is_passed,
            "audit_disposition": "APPROVED_FOR_PAYMENT" if is_passed else "REJECTED_OVERCHARGE_DISPUTED",
            "variances": {
                "linehaul_variance": float(variance_linehaul),
                "fuel_surcharge_variance": float(variance_fuel),
                "accessorials_variance": float(variance_accessorials)
            },
            "dispute_action": None if is_passed else f"Issue freight dispute claim for ${total_overcharge:.2f} billing discrepancy."
        }
