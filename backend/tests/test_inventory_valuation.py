"""
NexERP Inventory & FIFO / Moving Average Costing Test Suite.
Verifies queue depletion, inventory layer valuation, and stock balance tracking.
"""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import InsufficientStockError
from backend.src.modules.inventory.models import UnitOfMeasure, ItemCategory, Item, Warehouse, WarehouseLocation
from backend.src.modules.inventory.services import CostingValuationService, StockMovementService
from backend.src.modules.inventory.schemas import StockMovementCreate, StockMovementLineCreate
from backend.src.modules.inventory.enums import MovementType


@pytest.mark.asyncio
async def test_fifo_layer_depletion_chronological_sequence(db_session: AsyncSession):
    """
    Ensure FIFO cost layers are consumed in strict chronological order (oldest layer first).
    """
    tenant_id = "org_corp_hq_001"

    uom = UnitOfMeasure(tenant_id=tenant_id, code="EA", name="Units", category="Quantity")
    cat = ItemCategory(tenant_id=tenant_id, code="RAW", name="Raw Material", valuation_method="FIFO")
    wh = Warehouse(tenant_id=tenant_id, code="WH-01", name="Main Warehouse")
    db_session.add_all([uom, cat, wh])
    await db_session.flush()

    loc = WarehouseLocation(tenant_id=tenant_id, warehouse_id=wh.id, location_code="BIN-A1")
    db_session.add(loc)
    await db_session.flush()

    item = Item(
        tenant_id=tenant_id,
        sku="TEST-BEARING",
        name="Ball Bearing",
        category_id=cat.id,
        uom_id=uom.id,
        standard_cost=Decimal("10.00"),
        moving_average_cost=Decimal("10.00"),
        list_price=Decimal("20.00")
    )
    db_session.add(item)
    await db_session.commit()

    # 1. Receipt Layer 1: 10 units @ $10.00 on Jan 1
    await CostingValuationService.record_receipt_layer(
        db_session, tenant_id, item.id, Decimal("10.0"), Decimal("10.00"), date(2026, 1, 1), "GRN-01"
    )

    # 2. Receipt Layer 2: 10 units @ $15.00 on Jan 5
    await CostingValuationService.record_receipt_layer(
        db_session, tenant_id, item.id, Decimal("10.0"), Decimal("15.00"), date(2026, 1, 5), "GRN-02"
    )

    # 3. Issue 15 units on Jan 10
    # Expected COGS: 10 @ $10.00 ($100) + 5 @ $15.00 ($75) = $175.00 total ($11.6667 per unit)
    total_cogs, unit_cogs = await CostingValuationService.deplete_fifo_layers(
        db_session, tenant_id, item.id, Decimal("15.0")
    )

    assert total_cogs == Decimal("175.00")
    assert unit_cogs == Decimal("11.6667")

    # Verify remaining stock in Layer 2 is 5 units
    layers = await CostingValuationService.get_item_valuation_layers(db_session, tenant_id, item.id)
    assert len(layers) == 2
    assert layers[0].remaining_quantity == Decimal("0.0")  # Jan 1 layer fully depleted
    assert layers[1].remaining_quantity == Decimal("5.0")  # Jan 5 layer has 5 left


@pytest.mark.asyncio
async def test_moving_average_cost_recalculation(db_session: AsyncSession):
    """
    Ensure Moving Weighted Average cost recalculates accurately:
    ((Old_Qty * Old_Avg) + (New_Qty * Unit_Cost)) / (Old_Qty + New_Qty)
    """
    tenant_id = "org_corp_hq_001"

    uom = UnitOfMeasure(tenant_id=tenant_id, code="EA", name="Units", category="Quantity")
    cat = ItemCategory(tenant_id=tenant_id, code="ELEC", name="Electronics", valuation_method="MOVING_AVERAGE")
    db_session.add_all([uom, cat])
    await db_session.flush()

    item = Item(
        tenant_id=tenant_id,
        sku="TEST-RESISTOR",
        name="10k Resistor",
        category_id=cat.id,
        uom_id=uom.id,
        standard_cost=Decimal("2.00"),
        moving_average_cost=Decimal("2.00"),
        list_price=Decimal("5.00")
    )
    db_session.add(item)
    await db_session.commit()

    # Initial: 100 units @ $2.00 = $200
    # Add: 50 units @ $5.00 = $250
    # Expected New Average: (200 + 250) / 150 = 450 / 150 = $3.00
    new_avg = await CostingValuationService.recalculate_moving_average_cost(
        db_session,
        tenant_id=tenant_id,
        item_id=item.id,
        current_total_quantity=Decimal("100.0"),
        new_receipt_quantity=Decimal("50.0"),
        new_receipt_unit_cost=Decimal("5.00")
    )

    assert new_avg == Decimal("3.0000")
    await db_session.refresh(item)
    assert item.moving_average_cost == Decimal("3.0000")


@pytest.mark.asyncio
async def test_insufficient_stock_movement_rejection(db_session: AsyncSession):
    """
    Ensure stock movement engine rejects goods issue if stock balance is insufficient.
    """
    tenant_id = "org_corp_hq_001"

    uom = UnitOfMeasure(tenant_id=tenant_id, code="EA", name="Units", category="Quantity")
    cat = ItemCategory(tenant_id=tenant_id, code="RAW", name="Raw", valuation_method="FIFO")
    wh = Warehouse(tenant_id=tenant_id, code="WH-01", name="Main Warehouse")
    db_session.add_all([uom, cat, wh])
    await db_session.flush()

    loc = WarehouseLocation(tenant_id=tenant_id, warehouse_id=wh.id, location_code="BIN-A1")
    db_session.add(loc)
    await db_session.flush()

    item = Item(
        tenant_id=tenant_id,
        sku="TEST-VALVE",
        name="Valve",
        category_id=cat.id,
        uom_id=uom.id,
        standard_cost=Decimal("50.00"),
        moving_average_cost=Decimal("50.00"),
        list_price=Decimal("100.00")
    )
    db_session.add(item)
    await db_session.commit()

    # Attempt to issue 10 units when available is 0
    issue_payload = StockMovementCreate(
        movement_type=MovementType.GOODS_ISSUE,
        movement_date=date(2026, 1, 15),
        source_warehouse_id=wh.id,
        reference="ISSUE-001",
        lines=[
            StockMovementLineCreate(
                item_id=item.id,
                source_location_id=loc.id,
                quantity=Decimal("10.0")
            )
        ]
    )

    with pytest.raises(InsufficientStockError):
        await StockMovementService.execute_movement(db_session, tenant_id, issue_payload, "tester")
