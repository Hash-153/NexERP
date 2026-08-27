"""
NexERP Engineering Change Order (ECO / ECN) & BOM Revision Lifecycle Engine.
Manages formal engineering change requests, impact analysis on open Work Orders and POs,
redline BOM side-by-side diffing, and phased effectivity rollout.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.manufacturing.models import BillOfMaterials, BOMLine
from backend.src.modules.inventory.models import Item


class EngineeringChangeService:
    """
    Engineering Change Management (ECM) Service.
    """

    @classmethod
    def generate_bom_redline_diff(
        cls,
        old_bom_lines: List[Dict],
        new_bom_lines: List[Dict]
    ) -> Dict:
        """
        Compare current active BOM against proposed revision to produce redline diff
        (Added components, Removed components, Modified quantities/scrap rates).
        """
        old_map = {l["item_id"]: l for l in old_bom_lines}
        new_map = {l["item_id"]: l for l in new_bom_lines}

        added = []
        removed = []
        modified = []
        unchanged = []

        # Find added and modified
        for item_id, n_line in new_map.items():
            if item_id not in old_map:
                added.append({
                    "item_id": item_id,
                    "sku": n_line.get("sku", "ITEM"),
                    "name": n_line.get("name", "New Component"),
                    "new_quantity": float(n_line["quantity"]),
                    "change_type": "ADDED"
                })
            else:
                o_line = old_map[item_id]
                o_qty = Decimal(str(o_line["quantity"]))
                n_qty = Decimal(str(n_line["quantity"]))
                o_scrap = Decimal(str(o_line.get("scrap_percentage", 0.0)))
                n_scrap = Decimal(str(n_line.get("scrap_percentage", 0.0)))

                if o_qty != n_qty or o_scrap != n_scrap:
                    modified.append({
                        "item_id": item_id,
                        "sku": n_line.get("sku", o_line.get("sku", "ITEM")),
                        "old_quantity": float(o_qty),
                        "new_quantity": float(n_qty),
                        "old_scrap_percent": float(o_scrap),
                        "new_scrap_percent": float(n_scrap),
                        "change_type": "MODIFIED"
                    })
                else:
                    unchanged.append(n_line)

        # Find removed
        for item_id, o_line in old_map.items():
            if item_id not in new_map:
                removed.append({
                    "item_id": item_id,
                    "sku": o_line.get("sku", "ITEM"),
                    "name": o_line.get("name", "Obsolete Component"),
                    "old_quantity": float(o_line["quantity"]),
                    "change_type": "REMOVED"
                })

        return {
            "total_changes": len(added) + len(removed) + len(modified),
            "added_components": added,
            "removed_components": removed,
            "modified_components": modified,
            "unchanged_components_count": len(unchanged)
        }
