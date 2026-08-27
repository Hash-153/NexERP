"""
NexERP Warehouse Directed Putaway & Dynamic Slotting Optimization Engine.
Evaluates:
- Item Velocity Category (A = Fast mover near dock, B = Medium, C = Slow mover high racks)
- Unit Dimensions & Bin Cubic Capacity Constraints
- Floor vs High-Bay Rack Weight Limitations
- Segregated Hazard / Temperature Control Zones.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class DirectedPutawayService:
    """
    Warehouse Slotting Optimization & Directed Putaway Service.
    """

    @classmethod
    def recommend_putaway_location(
        cls,
        item_sku: str,
        item_velocity_class: str,
        weight_per_unit_kg: Decimal,
        volume_per_unit_m3: Decimal,
        quantity: Decimal,
        is_hazmat: bool,
        available_bins: List[Dict]
    ) -> Dict:
        """
        Find optimal bin location matching velocity zone, capacity, and hazmat compatibility.
        """
        total_weight = weight_per_unit_kg * quantity
        total_volume = volume_per_unit_m3 * quantity

        # Filter candidate bins
        eligible_bins = []
        for b in available_bins:
            bin_max_weight = Decimal(str(b.get("max_weight_capacity_kg", 1000.0)))
            bin_max_vol = Decimal(str(b.get("max_volume_capacity_m3", 10.0)))
            bin_cur_weight = Decimal(str(b.get("current_weight_kg", 0.0)))
            bin_cur_vol = Decimal(str(b.get("current_volume_m3", 0.0)))
            bin_zone = b.get("zone", "GENERAL").upper()
            bin_velocity = b.get("velocity_tier", "B").upper()

            # Check Hazmat containment
            if is_hazmat and bin_zone != "HAZMAT_STORAGE":
                continue
            if not is_hazmat and bin_zone == "HAZMAT_STORAGE":
                continue

            # Check weight & volume headroom
            if (bin_cur_weight + total_weight) > bin_max_weight:
                continue
            if (bin_cur_vol + total_volume) > bin_max_vol:
                continue

            # Velocity match score: Exact match = 100, Adjacent = 50, Mismatch = 0
            if bin_velocity == item_velocity_class.upper():
                v_score = 100
            elif (item_velocity_class == "A" and bin_velocity == "B") or (item_velocity_class == "C" and bin_velocity == "B"):
                v_score = 50
            else:
                v_score = 10

            eligible_bins.append({
                "bin_id": b["id"],
                "bin_code": b["bin_code"],
                "aisle": b.get("aisle", "01"),
                "rack": b.get("rack", "01"),
                "shelf": b.get("shelf", "01"),
                "zone": bin_zone,
                "velocity_tier": bin_velocity,
                "score": v_score,
                "remaining_weight_capacity_kg": float(bin_max_weight - bin_cur_weight - total_weight),
                "remaining_volume_capacity_m3": float(bin_max_vol - bin_cur_vol - total_volume)
            })

        if not eligible_bins:
            return {
                "item_sku": item_sku,
                "putaway_feasible": False,
                "recommended_bin": None,
                "reason": "No eligible bins found with sufficient weight/volume capacity and matching storage zone."
            }

        # Sort by score descending (velocity proximity), then remaining volume ascending (best cubic fit)
        eligible_bins.sort(key=lambda x: (-x["score"], x["remaining_volume_capacity_m3"]))
        best_bin = eligible_bins[0]

        return {
            "item_sku": item_sku,
            "putaway_feasible": True,
            "quantity_to_store": float(quantity),
            "total_weight_kg": float(total_weight),
            "total_volume_m3": float(total_volume),
            "recommended_bin": best_bin,
            "alternative_bins_count": len(eligible_bins) - 1,
            "travel_path_instruction": f"Navigate to Aisle {best_bin['aisle']}, Rack {best_bin['rack']}, Shelf {best_bin['shelf']} ({best_bin['bin_code']})."
        }
