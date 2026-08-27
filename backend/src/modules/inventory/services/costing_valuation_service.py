"""
NexERP Inventory Valuation & FIFO Layer Depletion Engine.
Implements GAAP/IFRS compliant FIFO lot queue consumption and Moving Weighted Average cost recalculation.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import InsufficientStockError, StockValuationError
from backend.src.modules.inventory.models import (
    Item,
    ItemCategory,
    StockValuationLayer,
    StockItemBalance
)
from backend.src.modules.inventory.enums import ValuationMethod


class CostingValuationService:
    """
    Inventory Cost Accounting Service.
    """

    @classmethod
    async def record_receipt_valuation(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str,
        warehouse_id: str,
        quantity: Decimal,
        unit_cost: Decimal,
        receipt_date: date,
        lot_id: Optional[str] = None,
        source_doc_type: Optional[str] = None,
        source_doc_id: Optional[str] = None
    ) -> StockValuationLayer:
        """
        Record receipt into FIFO valuation layer and update Item moving average cost.
        """
        # Fetch item & category
        item_res = await db.execute(select(Item).where(Item.id == item_id, Item.tenant_id == tenant_id))
        item = item_res.scalar_one()

        # Update Moving Average Cost:
        # Total Current Quantity in tenant
        bal_res = await db.execute(
            select(StockItemBalance)
            .where(StockItemBalance.item_id == item_id, StockItemBalance.tenant_id == tenant_id)
        )
        total_existing_qty = sum(b.quantity_on_hand for b in bal_res.scalars().all())

        if total_existing_qty + quantity > Decimal("0.0"):
            current_total_value = total_existing_qty * item.moving_average_cost
            new_incoming_value = quantity * unit_cost
            new_avg = (current_total_value + new_incoming_value) / (total_existing_qty + quantity)
            item.moving_average_cost = new_avg.quantize(Decimal("0.0001"))

        # Create FIFO Valuation Layer
        layer = StockValuationLayer(
            tenant_id=tenant_id,
            item_id=item_id,
            warehouse_id=warehouse_id,
            lot_id=lot_id,
            receipt_date=receipt_date,
            initial_quantity=quantity,
            remaining_quantity=quantity,
            unit_cost=unit_cost,
            total_value=quantity * unit_cost,
            source_document_type=source_doc_type,
            source_document_id=source_doc_id
        )
        db.add(layer)
        await db.flush()
        return layer

    @classmethod
    async def record_receipt_layer(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str,
        quantity: Decimal,
        unit_cost: Decimal,
        receipt_date: date,
        reference: Optional[str] = None,
        warehouse_id: Optional[str] = None
    ) -> StockValuationLayer:
        layer = StockValuationLayer(
            tenant_id=tenant_id,
            item_id=item_id,
            warehouse_id=warehouse_id or "WH-DEFAULT",
            receipt_date=receipt_date,
            initial_quantity=quantity,
            remaining_quantity=quantity,
            unit_cost=unit_cost,
            total_value=quantity * unit_cost,
            source_document_type="GoodsReceipt",
            source_document_id=reference
        )
        db.add(layer)
        await db.flush()
        return layer

    @classmethod
    async def get_item_valuation_layers(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str
    ) -> List[StockValuationLayer]:
        query = (
            select(StockValuationLayer)
            .where(StockValuationLayer.item_id == item_id, StockValuationLayer.tenant_id == tenant_id)
            .order_by(StockValuationLayer.receipt_date.asc(), StockValuationLayer.created_at.asc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def recalculate_moving_average_cost(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str,
        current_total_quantity: Decimal,
        new_receipt_quantity: Decimal,
        new_receipt_unit_cost: Decimal
    ) -> Decimal:
        item_res = await db.execute(select(Item).where(Item.id == item_id, Item.tenant_id == tenant_id))
        item = item_res.scalar_one()

        current_val = current_total_quantity * item.moving_average_cost
        new_val = new_receipt_quantity * new_receipt_unit_cost
        total_q = current_total_quantity + new_receipt_quantity

        new_avg = (current_val + new_val) / total_q if total_q > 0 else item.moving_average_cost
        new_avg = new_avg.quantize(Decimal("0.0001"))
        item.moving_average_cost = new_avg
        await db.flush()
        return new_avg

    @classmethod
    async def deplete_fifo_layers(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str,
        quantity_to_deplete: Decimal,
        warehouse_id: Optional[str] = None
    ) -> Tuple[Decimal, Decimal]:
        """
        Deplete inventory cost layers in strict First-In, First-Out (FIFO) chronological sequence.
        Returns (total_cost_consumed, unit_cost_consumed).
        """
        query = (
            select(StockValuationLayer)
            .where(
                StockValuationLayer.item_id == item_id,
                StockValuationLayer.tenant_id == tenant_id,
                StockValuationLayer.remaining_quantity > Decimal("0.0")
            )
        )
        if warehouse_id:
            query = query.where(StockValuationLayer.warehouse_id == warehouse_id)
        query = query.order_by(StockValuationLayer.receipt_date.asc(), StockValuationLayer.created_at.asc())
        
        result = await db.execute(query)
        layers = list(result.scalars().all())

        available_qty = sum(l.remaining_quantity for l in layers)
        if available_qty < quantity_to_deplete:
            raise InsufficientStockError(
                f"Cannot deplete {quantity_to_deplete} units. Available FIFO layer stock is only {available_qty} units."
            )

        total_cost_consumed = Decimal("0.0")
        remaining_to_deplete = quantity_to_deplete

        for layer in layers:
            if remaining_to_deplete <= Decimal("0.0"):
                break

            take_qty = min(layer.remaining_quantity, remaining_to_deplete)
            layer_cost = take_qty * layer.unit_cost
            total_cost_consumed += layer_cost

            layer.remaining_quantity = layer.remaining_quantity - take_qty
            layer.total_value = layer.remaining_quantity * layer.unit_cost
            remaining_to_deplete -= take_qty

        unit_cost_consumed = (total_cost_consumed / quantity_to_deplete).quantize(Decimal("0.0001"))
        await db.flush()
        return total_cost_consumed, unit_cost_consumed
