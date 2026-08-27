"""
Perpetual Inventory Valuation Layer Engine (FIFO, LIFO Layer Pools, and Moving Weighted Average).
"""
from decimal import Decimal
from typing import Dict, Any, List

class AdvancedInventoryCostingEngine:
    @staticmethod
    def consume_fifo_layers(
        fifo_layers: List[Dict[str, Decimal]], # [{"layer_id": "L1", "quantity": 100, "unit_cost": 25.0}]
        quantity_to_consume: Decimal
    ) -> Dict[str, Any]:
        """Consumes inventory layers in strict First-In First-Out FIFO sequence."""
        remaining_qty_to_pick = quantity_to_consume
        total_cogs = Decimal("0.0")
        consumed_layers = []
        updated_layers = []

        for layer in fifo_layers:
            layer_qty = layer["quantity"]
            layer_cost = layer["unit_cost"]

            if remaining_qty_to_pick <= 0:
                updated_layers.append(dict(layer))
                continue

            if layer_qty <= remaining_qty_to_pick:
                # Fully consume layer
                cogs_part = layer_qty * layer_cost
                total_cogs += cogs_part
                consumed_layers.append({
                    "layer_id": layer["layer_id"],
                    "consumed_qty": float(layer_qty),
                    "unit_cost": float(layer_cost),
                    "extended_cost": float(cogs_part)
                })
                remaining_qty_to_pick -= layer_qty
            else:
                # Partially consume layer
                cogs_part = remaining_qty_to_pick * layer_cost
                total_cogs += cogs_part
                consumed_layers.append({
                    "layer_id": layer["layer_id"],
                    "consumed_qty": float(remaining_qty_to_pick),
                    "unit_cost": float(layer_cost),
                    "extended_cost": float(cogs_part)
                })
                updated_layers.append({
                    "layer_id": layer["layer_id"],
                    "quantity": layer_qty - remaining_qty_to_pick,
                    "unit_cost": layer_cost
                })
                remaining_qty_to_pick = Decimal("0.0")

        avg_unit_cogs = (total_cogs / quantity_to_consume).quantize(Decimal("0.01")) if quantity_to_consume > 0 else Decimal("0.0")

        return {
            "requested_consumption_quantity": float(quantity_to_consume),
            "unfulfilled_stockout_shortage": float(remaining_qty_to_pick),
            "total_cogs_cost_of_goods_sold": float(total_cogs.quantize(Decimal("0.01"))),
            "effective_unit_cogs": float(avg_unit_cogs),
            "consumed_layers": consumed_layers,
            "remaining_inventory_layers": [
                {"layer_id": l["layer_id"], "quantity": float(l["quantity"]), "unit_cost": float(l["unit_cost"])}
                for l in updated_layers
            ]
        }
