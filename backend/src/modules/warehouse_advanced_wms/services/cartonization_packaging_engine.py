"""
3D Bin Packing & Cartonization Optimization Engine.
Selects the minimum cost shipping carton and calculates void fill percentage.
"""
from decimal import Decimal
from typing import Dict, Any, List

class CartonizationPackagingEngine:
    STANDARD_CARTONS = [
        {"box_type": "BOX_SMALL_S1", "l_cm": Decimal("20.0"), "w_cm": Decimal("15.0"), "h_cm": Decimal("10.0"), "max_wt_kg": Decimal("5.0"), "cost": Decimal("0.85")},
        {"box_type": "BOX_MEDIUM_M2", "l_cm": Decimal("35.0"), "w_cm": Decimal("25.0"), "h_cm": Decimal("20.0"), "max_wt_kg": Decimal("15.0"), "cost": Decimal("1.45")},
        {"box_type": "BOX_LARGE_L3", "l_cm": Decimal("50.0"), "w_cm": Decimal("40.0"), "h_cm": Decimal("30.0"), "max_wt_kg": Decimal("30.0"), "cost": Decimal("2.80")},
        {"box_type": "BOX_HEAVY_PALLET_CUBE", "l_cm": Decimal("120.0"), "w_cm": Decimal("80.0"), "h_cm": Decimal("100.0"), "max_wt_kg": Decimal("500.0"), "cost": Decimal("18.50")},
    ]

    @classmethod
    def optimize_order_carton(cls, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_vol = sum(
            Decimal(str(it.get("l_cm", 10))) * Decimal(str(it.get("w_cm", 10))) * Decimal(str(it.get("h_cm", 10))) * Decimal(str(it.get("quantity", 1)))
            for it in items
        )
        total_wt = sum(Decimal(str(it.get("weight_kg", 0.5))) * Decimal(str(it.get("quantity", 1))) for it in items)

        selected_carton = cls.STANDARD_CARTONS[-1]
        for carton in cls.STANDARD_CARTONS:
            carton_vol = carton["l_cm"] * carton["w_cm"] * carton["h_cm"]
            # 85% packing efficiency factor accounting for irregular shape geometry
            usable_vol = carton_vol * Decimal("0.85")
            if usable_vol >= total_vol and carton["max_wt_kg"] >= total_wt:
                selected_carton = carton
                break

        carton_total_vol = selected_carton["l_cm"] * selected_carton["w_cm"] * selected_carton["h_cm"]
        void_fill_vol = max(Decimal("0.0"), carton_total_vol - total_vol)
        void_pct = ((void_fill_vol / carton_total_vol) * Decimal("100.0")).quantize(Decimal("0.01")) if carton_total_vol > 0 else Decimal("0.0")

        return {
            "selected_box_type": selected_carton["box_type"],
            "box_dimensions_cm": f"{selected_carton['l_cm']}x{selected_carton['w_cm']}x{selected_carton['h_cm']}",
            "box_unit_cost": float(selected_carton["cost"]),
            "gross_weight_kg": float(total_wt),
            "packed_items_volume_cm3": float(total_vol),
            "carton_capacity_cm3": float(carton_total_vol),
            "void_fill_percentage": float(void_pct),
            "dunnage_required": bool(void_pct > Decimal("15.0"))
        }
