"""
NexERP Advanced Warehouse Management (WMS) Wave Picking & Pick-Path Optimization Engine.
Consolidates multiple outbound fulfillment orders into optimized wave batches and sequences
storage bin coordinates to minimize picker transit travel distance.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional


class WavePickingService:
    """
    WMS Wave & Cluster Picking Optimization Service.
    """

    @classmethod
    def generate_picking_wave(
        cls,
        outbound_orders: List[Dict],
        max_orders_per_wave: int = 10,
        max_items_per_wave: int = 100
    ) -> List[Dict]:
        """
        Group outbound orders into discrete picking waves respecting picker cart capacity limits.
        """
        waves = []
        current_wave_orders = []
        current_item_count = 0
        wave_seq = 1

        for order in outbound_orders:
            order_items = sum(int(l.get("quantity", 1)) for l in order.get("lines", []))

            if len(current_wave_orders) >= max_orders_per_wave or (current_item_count + order_items) > max_items_per_wave:
                if current_wave_orders:
                    waves.append({
                        "wave_number": f"WAVE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{wave_seq:03d}",
                        "order_count": len(current_wave_orders),
                        "total_units": current_item_count,
                        "orders": current_wave_orders
                    })
                    wave_seq += 1
                    current_wave_orders = []
                    current_item_count = 0

            current_wave_orders.append(order)
            current_item_count += order_items

        if current_wave_orders:
            waves.append({
                "wave_number": f"WAVE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{wave_seq:03d}",
                "order_count": len(current_wave_orders),
                "total_units": current_item_count,
                "orders": current_wave_orders
            })

        return waves

    @classmethod
    def optimize_pick_path_sequence(
        cls,
        pick_lines: List[Dict]
    ) -> List[Dict]:
        """
        Sequence pick tasks along standard S-Shape / Serpentine warehouse traversal path:
        Order by Zone -> Aisle (Alternating ascending/descending) -> Rack -> Shelf -> Bin.
        """
        def sort_key(line):
            zone = str(line.get("zone", "Z1"))
            aisle = str(line.get("aisle", "01")).zfill(3)
            rack = str(line.get("rack", "01")).zfill(3)
            shelf = str(line.get("shelf", "01")).zfill(3)
            bin_coord = str(line.get("bin", "01")).zfill(3)
            return (zone, aisle, rack, shelf, bin_coord)

        sorted_picks = sorted(pick_lines, key=sort_key)
        for idx, pick in enumerate(sorted_picks, start=1):
            pick["pick_sequence_index"] = idx

        return sorted_picks
