"""
Landed Cost Allocation & Customs Duty Absorption Engine.
Apportions ocean freight, customs tariffs, port drayage, and marine insurance across shipment receipt lines.
"""
from decimal import Decimal
from typing import Dict, Any, List

class LandedCostAllocationEngine:
    @staticmethod
    def allocate_landed_costs(
        shipment_lines: List[Dict[str, Any]],
        total_freight_cost: Decimal,
        total_customs_duties: Decimal,
        total_insurance_cost: Decimal,
        allocation_method: str = "VALUE" # VALUE, WEIGHT, VOLUME
    ) -> List[Dict[str, Any]]:
        total_pool = total_freight_cost + total_customs_duties + total_insurance_cost
        
        if allocation_method == "WEIGHT":
            total_basis = sum(Decimal(str(l.get("weight_kg", 1))) * Decimal(str(l.get("quantity", 1))) for l in shipment_lines)
        elif allocation_method == "VOLUME":
            total_basis = sum(Decimal(str(l.get("volume_cbm", 0.01))) * Decimal(str(l.get("quantity", 1))) for l in shipment_lines)
        else:
            total_basis = sum(Decimal(str(l.get("unit_po_price", 1))) * Decimal(str(l.get("quantity", 1))) for l in shipment_lines)

        results = []
        for line in shipment_lines:
            qty = Decimal(str(line.get("quantity", 1)))
            unit_price = Decimal(str(line.get("unit_po_price", 1)))
            ext_price = qty * unit_price
            
            if allocation_method == "WEIGHT":
                line_basis = Decimal(str(line.get("weight_kg", 1))) * qty
            elif allocation_method == "VOLUME":
                line_basis = Decimal(str(line.get("volume_cbm", 0.01))) * qty
            else:
                line_basis = ext_price

            share_pct = line_basis / total_basis if total_basis > 0 else Decimal("0.0")
            allocated_landed = (total_pool * share_pct).quantize(Decimal("0.01"))
            allocated_unit_landed = (allocated_landed / qty).quantize(Decimal("0.01")) if qty > 0 else Decimal("0.0")
            final_unit_cost = unit_price + allocated_unit_landed

            results.append({
                "item_sku": line.get("sku", "UNKNOWN"),
                "quantity": float(qty),
                "base_po_unit_price": float(unit_price),
                "allocated_landed_cost_total": float(allocated_landed),
                "allocated_landed_cost_per_unit": float(allocated_unit_landed),
                "effective_capitalized_unit_cost": float(final_unit_cost),
                "cost_markup_percentage": float(((allocated_unit_landed / unit_price) * Decimal("100.0")).quantize(Decimal("0.01"))) if unit_price > 0 else 0.0
            })

        return results
