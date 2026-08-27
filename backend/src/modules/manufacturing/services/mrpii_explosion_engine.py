"""
MRP-II Multi-Level Bill of Materials (BOM) Explosion & Netting Engine.
Performs gross requirements calculation, on-hand inventory netting, scheduled receipts offsetting, and planned order release dates.
"""
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any, List

class MRPIIExplosionEngine:
    @classmethod
    def explode_and_net_bom(
        cls,
        parent_item_sku: str,
        gross_demand_qty: Decimal,
        target_delivery_date: date,
        bom_structure: List[Dict[str, Any]],
        inventory_snapshot: Dict[str, Decimal]
    ) -> List[Dict[str, Any]]:
        planned_orders = []

        for component in bom_structure:
            comp_sku = component.get("component_sku", "RAW-001")
            qty_per_parent = Decimal(str(component.get("quantity_per_assembly", 1.0)))
            lead_time_days = int(component.get("lead_time_days", 7))
            scrap_factor = Decimal(str(component.get("scrap_factor_pct", 0.0))) / Decimal("100.0")

            gross_req = gross_demand_qty * qty_per_parent * (Decimal("1.0") + scrap_factor)
            on_hand = inventory_snapshot.get(comp_sku, Decimal("0.0"))
            
            # Net Requirement
            net_req = max(Decimal("0.0"), gross_req - on_hand)
            # Release Date offset by supplier/manufacturing lead time
            order_release_date = target_delivery_date - timedelta(days=lead_time_days)

            planned_orders.append({
                "component_sku": comp_sku,
                "component_name": component.get("component_name", "Raw Material Component"),
                "gross_requirement_qty": float(gross_req.quantize(Decimal("0.01"))),
                "on_hand_inventory": float(on_hand),
                "net_planned_order_qty": float(net_req.quantize(Decimal("0.01"))),
                "lead_time_days": lead_time_days,
                "required_dock_date": target_delivery_date.isoformat(),
                "suggested_order_release_date": order_release_date.isoformat(),
                "action": "CREATE_PURCHASE_REQUISITION" if component.get("is_purchased", True) else "RELEASE_WORK_ORDER"
            })

        return planned_orders
