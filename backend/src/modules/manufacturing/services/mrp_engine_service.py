"""
NexERP Material Requirements Planning (MRP-II) Calculation Engine.
Executes Master Production Schedule (MPS) gross-to-net demand explosion, lead-time offsetting,
and generates suggested Purchase Orders and Production Work Orders.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.modules.manufacturing.models import (
    MRPSnapshot,
    MRPPlannedOrder,
    BillOfMaterials,
    BOMLine
)
from backend.src.modules.manufacturing.enums import MRPOrderType
from backend.src.modules.manufacturing.services.bom_service import BOMService
from backend.src.modules.inventory.models import Item, StockItemBalance
from backend.src.modules.inventory.enums import ItemType
from backend.src.modules.sales.models import SalesOrder, SalesOrderLine
from backend.src.modules.sales.enums import SalesOrderStatus


class MRPEngineService:
    """
    Core MRP-II Planning Algorithm Engine.
    """

    @classmethod
    async def run_mrp_calculation(
        cls,
        db: AsyncSession,
        tenant_id: str,
        planning_horizon_days: int = 90,
        user_id: Optional[str] = None
    ) -> MRPSnapshot:
        """
        Execute full MRP run across open demand and inventory balances:
        1. Aggregate Gross Requirements from Open Sales Orders and Safety Stock thresholds.
        2. Net against On-Hand Inventory balances.
        3. Explode multi-level BOMs for manufactured shortages.
        4. Offset by supplier/manufacturing lead-times.
        5. Persist planned order recommendations.
        """
        snapshot_date = date.today()
        snapshot = MRPSnapshot(
            tenant_id=tenant_id,
            snapshot_date=snapshot_date,
            status="COMPLETED",
            total_planned_orders=0,
            generated_by_id=user_id
        )
        db.add(snapshot)
        await db.flush()

        # 1. Fetch all items
        items_res = await db.execute(select(Item).where(Item.tenant_id == tenant_id, Item.is_deleted == False))
        items = {it.id: it for it in items_res.scalars().all()}

        # 2. Fetch current total on-hand balances per item
        bal_res = await db.execute(select(StockItemBalance).where(StockItemBalance.tenant_id == tenant_id))
        balances: Dict[str, Decimal] = {it_id: Decimal("0.0") for it_id in items.keys()}
        for b in bal_res.scalars().all():
            if b.item_id in balances:
                balances[b.item_id] += b.quantity_available

        # 3. Aggregate Gross Demand from open Sales Orders within planning horizon
        horizon_end = snapshot_date + timedelta(days=planning_horizon_days)
        so_query = (
            select(SalesOrderLine)
            .join(SalesOrder, SalesOrder.id == SalesOrderLine.sales_order_id)
            .where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status.in_([SalesOrderStatus.CONFIRMED.value, SalesOrderStatus.PROCESSING.value]),
                SalesOrder.requested_delivery_date <= horizon_end
            )
            .options(selectinload(SalesOrderLine.sales_order))
        )
        so_lines_res = await db.execute(so_query)
        so_lines = so_lines_res.scalars().all()

        gross_demand: Dict[str, List[Dict]] = {it_id: [] for it_id in items.keys()}
        for sol in so_lines:
            unfulfilled = sol.quantity_ordered - sol.quantity_fulfilled
            if unfulfilled > 0 and sol.item_id in gross_demand:
                gross_demand[sol.item_id].append({
                    "required_date": sol.sales_order.requested_delivery_date,
                    "quantity": unfulfilled,
                    "source_type": "SalesOrder",
                    "source_id": sol.sales_order.id
                })

        # 4. Check Safety Stock requirements
        for it_id, item in items.items():
            if balances[it_id] < item.safety_stock:
                shortage = item.safety_stock - balances[it_id]
                gross_demand[it_id].append({
                    "required_date": snapshot_date + timedelta(days=item.lead_time_days),
                    "quantity": shortage,
                    "source_type": "SafetyStockReplenishment",
                    "source_id": None
                })

        planned_orders = []

        # 5. Process Net Requirements & Explode BOMs
        for it_id, demands in gross_demand.items():
            item = items.get(it_id)
            if not item:
                continue

            available_inventory = balances.get(it_id, Decimal("0.0"))

            for demand in demands:
                demand_qty = demand["quantity"]
                req_date = demand["required_date"]

                if available_inventory >= demand_qty:
                    available_inventory -= demand_qty
                    balances[it_id] = available_inventory
                    continue

                # Net Shortage
                net_shortage = demand_qty - available_inventory
                available_inventory = Decimal("0.0")
                balances[it_id] = Decimal("0.0")

                # Lead-time offset
                lead_days = max(1, item.lead_time_days)
                suggested_order_date = max(snapshot_date, req_date - timedelta(days=lead_days))

                # Determine whether PURCHASE or PRODUCTION
                if item.item_type in [ItemType.RAW_MATERIAL.value, ItemType.CONSUMABLE.value]:
                    order_type = MRPOrderType.PURCHASE.value
                    est_cost = net_shortage * (item.standard_cost or item.moving_average_cost)
                else:
                    order_type = MRPOrderType.PRODUCTION.value
                    est_cost = net_shortage * (item.standard_cost or item.moving_average_cost)

                    # Trigger Dependent Demand BOM Explosion
                    exploded_subs = await BOMService.explode_bom_multi_level(
                        db=db,
                        tenant_id=tenant_id,
                        item_id=item.id,
                        demand_quantity=net_shortage
                    )
                    for sub in exploded_subs:
                        sub_it = items.get(sub["item_id"])
                        if sub_it:
                            sub_lead = max(1, sub_it.lead_time_days)
                            sub_order_date = max(snapshot_date, suggested_order_date - timedelta(days=sub_lead))
                            sub_type = MRPOrderType.PURCHASE.value if sub_it.item_type == ItemType.RAW_MATERIAL.value else MRPOrderType.PRODUCTION.value

                            p_sub = MRPPlannedOrder(
                                tenant_id=tenant_id,
                                mrp_snapshot_id=snapshot.id,
                                item_id=sub["item_id"],
                                order_type=sub_type,
                                suggested_order_date=sub_order_date,
                                required_date=suggested_order_date,
                                quantity=sub["quantity_required"],
                                estimated_cost=Decimal(str(sub["total_estimated_cost"])),
                                source_demand_type="DependentBOMDemand",
                                source_demand_id=item.id
                            )
                            db.add(p_sub)
                            planned_orders.append(p_sub)

                p_order = MRPPlannedOrder(
                    tenant_id=tenant_id,
                    mrp_snapshot_id=snapshot.id,
                    item_id=item.id,
                    order_type=order_type,
                    suggested_order_date=suggested_order_date,
                    required_date=req_date,
                    quantity=net_shortage,
                    estimated_cost=est_cost,
                    source_demand_type=demand["source_type"],
                    source_demand_id=demand["source_id"]
                )
                db.add(p_order)
                planned_orders.append(p_order)

        snapshot.total_planned_orders = len(planned_orders)
        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    @classmethod
    async def list_snapshots(cls, db: AsyncSession, tenant_id: str) -> List[MRPSnapshot]:
        query = (
            select(MRPSnapshot)
            .where(MRPSnapshot.tenant_id == tenant_id)
            .options(selectinload(MRPSnapshot.planned_orders))
            .order_by(MRPSnapshot.snapshot_date.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
