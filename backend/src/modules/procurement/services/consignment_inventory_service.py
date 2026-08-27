"""
NexERP Vendor Managed / Consignment Inventory (VMI) Engine.
Manages:
- Consignment Stock ownership tracking (Title remains with supplier until consumption)
- Consumption pull logging from manufacturing or sales
- Automated Vendor Self-Billing Invoices / Credit Memos upon consumption.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class ConsignmentInventoryService:
    """
    Vendor Managed Inventory (VMI) & Consignment Settlement Service.
    """

    @classmethod
    def log_consignment_consumption(
        cls,
        vendor_id: str,
        vendor_name: str,
        item_id: str,
        item_sku: str,
        consumed_quantity: Decimal,
        agreed_consignment_unit_price: Decimal,
        work_order_id: Optional[str] = None
    ) -> Dict:
        """
        Record consumption of vendor-owned consignment stock and compute settlement bill amount.
        """
        if consumed_quantity <= Decimal("0.0") or agreed_consignment_unit_price <= Decimal("0.0"):
            raise ValueError("Consumed quantity and unit price must be positive.")

        total_settlement = (consumed_quantity * agreed_consignment_unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "item_id": item_id,
            "item_sku": item_sku,
            "work_order_reference": work_order_id,
            "consumed_quantity": float(consumed_quantity),
            "unit_price": float(agreed_consignment_unit_price),
            "total_settlement_payable": float(total_settlement),
            "consumption_timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SETTLEMENT_PENDING",
            "gl_accounting": {
                "debit_account": "Raw Material Consumption / COGS",
                "credit_account": "Vendor Accounts Payable (Consignment)",
                "amount": float(total_settlement)
            }
        }
