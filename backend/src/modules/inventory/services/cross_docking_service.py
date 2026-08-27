"""
NexERP Warehouse Cross-Docking & Flow-Through Opportunity Engine.
Identifies inbound Goods Receipts (GRN) that match pending customer backorders,
enabling direct dock-to-dock routing without putaway storage delays.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class CrossDockingService:
    """
    Cross-Docking Flow-Through Fulfillment Service.
    """

    @classmethod
    def match_inbound_shipment_to_backorders(
        cls,
        inbound_item_id: str,
        inbound_sku: str,
        inbound_quantity_received: Decimal,
        pending_sales_backorders: List[Dict]
    ) -> Dict:
        """
        Allocate received inbound goods directly to oldest priority customer backorders.
        """
        remaining_qty = inbound_quantity_received
        allocated_backorders = []

        # Sort backorders by priority (HIGH first), then by order_date ascending (FIFO)
        priority_map = {"HIGH": 0, "NORMAL": 1, "LOW": 2}
        sorted_orders = sorted(
            pending_sales_backorders,
            key=lambda o: (priority_map.get(o.get("priority", "NORMAL"), 1), o.get("order_date", ""))
        )

        for bo in sorted_orders:
            if remaining_qty <= Decimal("0.0"):
                break

            needed = Decimal(str(bo["quantity_unfulfilled"]))
            alloc = min(remaining_qty, needed)

            allocated_backorders.append({
                "sales_order_id": bo["sales_order_id"],
                "sales_order_number": bo.get("sales_order_number"),
                "customer_name": bo.get("customer_name"),
                "allocated_quantity": float(alloc),
                "remaining_unfulfilled_after_crossdock": float(needed - alloc),
                "is_fully_satisfied": alloc == needed,
                "staging_dock_assigned": "STAGING_BAY_OUTBOUND_01"
            })

            remaining_qty -= alloc

        putaway_excess_qty = remaining_qty

        return {
            "item_id": inbound_item_id,
            "sku": inbound_sku,
            "total_inbound_quantity": float(inbound_quantity_received),
            "cross_docked_quantity": float(inbound_quantity_received - putaway_excess_qty),
            "excess_quantity_for_warehouse_putaway": float(putaway_excess_qty),
            "cross_dock_ratio_percent": float(((inbound_quantity_received - putaway_excess_qty) / inbound_quantity_received * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) if inbound_quantity_received > Decimal("0.0") else 0.0,
            "dispatched_backorders_count": len(allocated_backorders),
            "allocations": allocated_backorders
        }
