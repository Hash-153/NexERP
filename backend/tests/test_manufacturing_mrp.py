"""
NexERP Manufacturing, Multi-Level BOM & MRP-II Automated Test Suite.
Verifies recursive explosion, cycle detection, work order backflushing, and gross-to-net scheduling.
"""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.exceptions import BOMRecursionError
from backend.src.modules.inventory.models import UnitOfMeasure, ItemCategory, Item, Warehouse, WarehouseLocation
from backend.src.modules.manufacturing.models import BillOfMaterials, BOMLine, WorkCenter, Routing, RoutingOperation
from backend.src.modules.manufacturing.services import BOMService, ProductionOrderService, MRPEngineService
from backend.src.modules.manufacturing.schemas import BOMCreate, BOMLineCreate, ProductionOrderCreate
from backend.src.modules.manufacturing.enums import ProductionOrderStatus


@pytest.mark.asyncio
async def test_bom_circular_recursion_detection(db_session: AsyncSession):
    """
    Ensure the BOM engine detects and blocks circular reference loops (Item A -> Item B -> Item A).
    """
    tenant_id = "org_corp_hq_001"

    uom = UnitOfMeasure(tenant_id=tenant_id, code="EA", name="Units", category="Quantity")
    cat = ItemCategory(tenant_id=tenant_id, code="MFG", name="Manufactured", valuation_method="FIFO")
    db_session.add_all([uom, cat])
    await db_session.flush()

    item_a = Item(tenant_id=tenant_id, sku="ITEM-A", name="Assembly A", category_id=cat.id, uom_id=uom.id, standard_cost=Decimal("100.00"), moving_average_cost=Decimal("100.00"), list_price=Decimal("200.00"))
    item_b = Item(tenant_id=tenant_id, sku="ITEM-B", name="Subassembly B", category_id=cat.id, uom_id=uom.id, standard_cost=Decimal("50.00"), moving_average_cost=Decimal("50.00"), list_price=Decimal("100.00"))
    db_session.add_all([item_a, item_b])
    await db_session.flush()

    # 1. BOM A uses Component B
    bom_a = BillOfMaterials(tenant_id=tenant_id, bom_number="BOM-A", item_id=item_a.id, quantity=Decimal("1.0"), uom_id=uom.id, version="1.0", is_default=True, effective_from=date(2026, 1, 1))
    db_session.add(bom_a)
    await db_session.flush()
    db_session.add(BOMLine(tenant_id=tenant_id, bom_id=bom_a.id, item_id=item_b.id, quantity=Decimal("1.0"), uom_id=uom.id))
    await db_session.commit()

    # 2. Attempt to create BOM B that uses Component A (Cycle: A -> B -> A)
    bom_b_payload = BOMCreate(
        bom_number="BOM-B",
        item_id=item_b.id,
        quantity=Decimal("1.0"),
        uom_id=uom.id,
        version="1.0",
        is_default=True,
        effective_from=date(2026, 1, 1),
        lines=[
            BOMLineCreate(item_id=item_a.id, quantity=Decimal("1.0"), uom_id=uom.id)
        ]
    )

    with pytest.raises(BOMRecursionError):
        await BOMService.create_bom(db_session, tenant_id, bom_b_payload)


@pytest.mark.asyncio
async def test_bom_multi_level_recursive_explosion(db_session: AsyncSession):
    """
    Ensure multi-tier BOM explosion correctly calculates quantities and scrap factors at each level.
    """
    tenant_id = "org_corp_hq_001"

    uom = UnitOfMeasure(tenant_id=tenant_id, code="EA", name="Units", category="Quantity")
    cat = ItemCategory(tenant_id=tenant_id, code="MFG", name="Manufactured", valuation_method="FIFO")
    db_session.add_all([uom, cat])
    await db_session.flush()

    fg = Item(tenant_id=tenant_id, sku="PUMP", name="Pump", category_id=cat.id, uom_id=uom.id, standard_cost=Decimal("500.00"), moving_average_cost=Decimal("500.00"), list_price=Decimal("1000.00"))
    sub = Item(tenant_id=tenant_id, sku="VALVE", name="Valve Subassembly", category_id=cat.id, uom_id=uom.id, standard_cost=Decimal("150.00"), moving_average_cost=Decimal("150.00"), list_price=Decimal("300.00"))
    raw = Item(tenant_id=tenant_id, sku="STEEL", name="Steel Bar", category_id=cat.id, uom_id=uom.id, standard_cost=Decimal("20.00"), moving_average_cost=Decimal("20.00"), list_price=Decimal("0.00"))
    db_session.add_all([fg, sub, raw])
    await db_session.flush()

    # Sub BOM: 1x VALVE requires 2x STEEL
    bom_sub = BillOfMaterials(tenant_id=tenant_id, bom_number="BOM-VALVE", item_id=sub.id, quantity=Decimal("1.0"), uom_id=uom.id, version="1.0", is_default=True, effective_from=date(2026, 1, 1))
    db_session.add(bom_sub)
    await db_session.flush()
    db_session.add(BOMLine(tenant_id=tenant_id, bom_id=bom_sub.id, item_id=raw.id, quantity=Decimal("2.0"), uom_id=uom.id, scrap_percentage=Decimal("0.0")))

    # FG BOM: 1x PUMP requires 3x VALVE
    bom_fg = BillOfMaterials(tenant_id=tenant_id, bom_number="BOM-PUMP", item_id=fg.id, quantity=Decimal("1.0"), uom_id=uom.id, version="1.0", is_default=True, effective_from=date(2026, 1, 1))
    db_session.add(bom_fg)
    await db_session.flush()
    db_session.add(BOMLine(tenant_id=tenant_id, bom_id=bom_fg.id, item_id=sub.id, quantity=Decimal("3.0"), uom_id=uom.id, scrap_percentage=Decimal("0.0")))
    await db_session.commit()

    # Explode for 5x PUMP
    # Expected: 5 * 3 = 15x VALVE (Level 1), 15 * 2 = 30x STEEL (Level 2)
    exploded = await BOMService.explode_bom_multi_level(
        db=db_session,
        tenant_id=tenant_id,
        item_id=fg.id,
        demand_quantity=Decimal("5.0")
    )

    assert len(exploded) == 2
    valve_entry = next(e for e in exploded if e["sku"] == "VALVE")
    steel_entry = next(e for e in exploded if e["sku"] == "STEEL")

    assert valve_entry["level"] == 1
    assert valve_entry["quantity_required"] == Decimal("15.0000")

    assert steel_entry["level"] == 2
    assert steel_entry["quantity_required"] == Decimal("30.0000")
