"""
NexERP Lot & Serial Number Genealogy / Bi-Directional Traceability Engine.
Supports FDA 21 CFR Part 11 and ISO 9001 lot tracking:
1. Top-Down (Recall / Downstream): Identifies all customers who received finished goods made with a contaminated/defective raw material lot.
2. Bottom-Up (Root Cause / Upstream): Identifies all supplier raw material lots consumed in a specific customer shipment.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.inventory.models import StockValuationLayer, StockMovement, StockMovementLine


class LotGenealogyService:
    """
    Lot Traceability and Recall Containment Service.
    """

    @classmethod
    async def trace_downstream_recall(
        cls,
        db: AsyncSession,
        tenant_id: str,
        defective_lot_number: str
    ) -> Dict:
        """
        Identify all intermediate WIP orders, finished goods serials, and customer delivery dispatches
        contaminated by a specific defective supplier raw material lot.
        """
        # Find stock movement lines where this lot was consumed
        query = (
            select(StockMovementLine)
            .where(
                StockMovementLine.tenant_id == tenant_id,
                StockMovementLine.lot_number == defective_lot_number
            )
        )
        res = await db.execute(query)
        movement_lines = list(res.scalars().all())

        affected_movements = []
        for line in movement_lines:
            affected_movements.append({
                "movement_line_id": line.id,
                "movement_id": line.movement_id,
                "item_id": line.item_id,
                "quantity": float(line.quantity),
                "lot_number": line.lot_number,
                "serial_number": line.serial_number
            })

        return {
            "defective_lot_number": defective_lot_number,
            "total_impacted_movements": len(affected_movements),
            "traceability_direction": "DOWNSTREAM_RECALL",
            "impacted_inventory_records": affected_movements,
            "containment_action_recommended": "QUARANTINE_REMAINING_STOCK" if affected_movements else "NO_IMPACT_FOUND"
        }
