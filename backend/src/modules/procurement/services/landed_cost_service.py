"""
NexERP Landed Cost Allocation Engine.
Apportions secondary logistics and customs expenditures (ocean freight, customs duty, port drayage, insurance)
across physical inventory receipts based on value, weight, volume, or equal split.
Compliant with IAS 2 (Inventories - Cost of Purchase).
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.inventory.models import StockValuationLayer, Item
from backend.src.modules.procurement.models import GoodsReceiptNote, GoodsReceiptLine


class LandedCostService:
    """
    Landed Cost Allocation Service.
    """

    @classmethod
    def allocate_landed_costs(
        cls,
        receipt_lines: List[Dict],
        landed_cost_expenses: List[Dict],
        allocation_method: str = "BY_VALUE"
    ) -> List[Dict]:
        """
        Distribute landed cost charges across receipt lines and calculate new adjusted unit landed costs.
        """
        total_landed_expense = sum(Decimal(str(e["amount"])) for e in landed_cost_expenses)
        if total_landed_expense <= Decimal("0.0") or not receipt_lines:
            return receipt_lines

        # Calculate allocation basis
        if allocation_method == "BY_VALUE":
            total_basis = sum(
                (Decimal(str(l["quantity"])) * Decimal(str(l["unit_cost"])))
                for l in receipt_lines
            )
        elif allocation_method == "BY_WEIGHT":
            total_basis = sum(
                (Decimal(str(l["quantity"])) * Decimal(str(l.get("unit_weight_kg", "1.0"))))
                for l in receipt_lines
            )
        elif allocation_method == "BY_QUANTITY":
            total_basis = sum(Decimal(str(l["quantity"])) for l in receipt_lines)
        else:
            total_basis = sum(
                (Decimal(str(l["quantity"])) * Decimal(str(l["unit_cost"])))
                for l in receipt_lines
            )

        if total_basis == Decimal("0.0"):
            return receipt_lines

        allocated_results = []
        running_allocated = Decimal("0.0")

        for idx, line in enumerate(receipt_lines):
            qty = Decimal(str(line["quantity"]))
            orig_cost = Decimal(str(line["unit_cost"]))
            orig_total = qty * orig_cost

            if allocation_method == "BY_VALUE":
                line_basis = orig_total
            elif allocation_method == "BY_WEIGHT":
                line_basis = qty * Decimal(str(line.get("unit_weight_kg", "1.0")))
            elif allocation_method == "BY_QUANTITY":
                line_basis = qty
            else:
                line_basis = orig_total

            # Line share of landed costs
            if idx == len(receipt_lines) - 1:
                # Absorb remaining rounding difference
                line_landed_portion = total_landed_expense - running_allocated
            else:
                line_landed_portion = (total_landed_expense * (line_basis / total_basis)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                running_allocated += line_landed_portion

            total_landed_value = orig_total + line_landed_portion
            new_unit_landed_cost = (total_landed_value / qty).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

            allocated_results.append({
                "item_id": line.get("item_id"),
                "sku": line.get("sku"),
                "quantity": float(qty),
                "original_unit_cost": float(orig_cost),
                "allocated_landed_cost": float(line_landed_portion),
                "total_landed_value": float(total_landed_value),
                "new_unit_landed_cost": float(new_unit_landed_cost),
                "cost_increase_percent": float(((new_unit_landed_cost - orig_cost) / orig_cost * Decimal("100.0")).quantize(Decimal("0.01"))) if orig_cost > Decimal("0.0") else 0.0
            })

        return allocated_results

    @classmethod
    async def apply_landed_cost_to_valuation_layers(
        cls,
        db: AsyncSession,
        tenant_id: str,
        grn_id: str,
        landed_cost_expenses: List[Dict],
        allocation_method: str = "BY_VALUE"
    ) -> List[StockValuationLayer]:
        """
        Directly update inventory valuation layer unit costs for a posted Goods Receipt Note.
        """
        grn_res = await db.execute(
            select(GoodsReceiptNote).where(GoodsReceiptNote.id == grn_id, GoodsReceiptNote.tenant_id == tenant_id)
        )
        grn = grn_res.scalar_one_or_none()
        if not grn:
            raise EntityNotFoundError("Goods Receipt Note not found.")

        # Find valuation layers associated with this GRN
        layers_res = await db.execute(
            select(StockValuationLayer).where(
                StockValuationLayer.tenant_id == tenant_id,
                StockValuationLayer.source_document_type == "GoodsReceipt",
                StockValuationLayer.source_document_id == grn.grn_number
            )
        )
        layers = list(layers_res.scalars().all())
        if not layers:
            raise BusinessRuleViolationError("No inventory valuation layers found matching this Goods Receipt Note.")

        receipt_lines_data = [
            {
                "layer_id": l.id,
                "item_id": l.item_id,
                "quantity": l.initial_quantity,
                "unit_cost": l.unit_cost
            }
            for l in layers
        ]

        allocation = cls.allocate_landed_costs(receipt_lines_data, landed_cost_expenses, allocation_method)

        for l, alloc in zip(layers, allocation):
            new_unit_cost = Decimal(str(alloc["new_unit_landed_cost"]))
            l.unit_cost = new_unit_cost
            l.total_value = l.remaining_quantity * new_unit_cost

        await db.commit()
        return layers
