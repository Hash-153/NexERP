"""
NexERP Physical Inventory Cycle Counting & Audit Service.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.inventory.models import (
    Warehouse,
    Item,
    StockItemBalance,
    CycleCountSheet,
    CycleCountLine
)
from backend.src.modules.inventory.schemas import CycleCountSheetCreate
from backend.src.modules.inventory.enums import CycleCountStatus, MovementType
from backend.src.modules.inventory.services.stock_movement_service import StockMovementService
from backend.src.modules.inventory.schemas import StockMovementCreate, StockMovementLineCreate


class CycleCountService:
    """
    Physical stock audit and reconciliation manager.
    """

    @classmethod
    async def create_count_sheet(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: CycleCountSheetCreate,
        user_id: Optional[str] = None
    ) -> CycleCountSheet:
        """
        Generate physical cycle count sheet with current system book balances.
        """
        year_str = str(payload.count_date.year)
        sheet_num = f"CC-{year_str}-{date.today().strftime('%m%d%H%M%S')}"

        sheet = CycleCountSheet(
            tenant_id=tenant_id,
            sheet_number=sheet_num,
            warehouse_id=payload.warehouse_id,
            count_date=payload.count_date,
            status=CycleCountStatus.DRAFT.value,
            supervisor_id=user_id,
            notes=payload.notes
        )
        db.add(sheet)
        await db.flush()

        for line_data in payload.lines:
            # Query system balance
            bal_query = select(StockItemBalance).where(
                StockItemBalance.tenant_id == tenant_id,
                StockItemBalance.warehouse_id == payload.warehouse_id,
                StockItemBalance.item_id == line_data.item_id,
                StockItemBalance.location_id == line_data.location_id,
                StockItemBalance.lot_id == line_data.lot_id
            )
            bal_res = await db.execute(bal_query)
            bal = bal_res.scalar_one_or_none()
            sys_qty = bal.quantity_on_hand if bal else Decimal("0.0")

            item_res = await db.execute(select(Item).where(Item.id == line_data.item_id))
            item = item_res.scalar_one()

            var_qty = line_data.counted_quantity - sys_qty
            var_cost = var_qty * item.moving_average_cost

            cc_line = CycleCountLine(
                tenant_id=tenant_id,
                sheet_id=sheet.id,
                item_id=line_data.item_id,
                location_id=line_data.location_id,
                lot_id=line_data.lot_id,
                system_quantity=sys_qty,
                counted_quantity=line_data.counted_quantity,
                variance_quantity=var_qty,
                unit_cost=item.moving_average_cost,
                variance_cost=var_cost
            )
            db.add(cc_line)

        await db.commit()
        await db.refresh(sheet)
        return sheet

    @classmethod
    async def approve_and_adjust_sheet(
        cls,
        db: AsyncSession,
        tenant_id: str,
        sheet_id: str,
        user_id: str
    ) -> CycleCountSheet:
        """
        Approve cycle count sheet and trigger automated positive/negative inventory adjustments.
        """
        query = (
            select(CycleCountSheet)
            .where(CycleCountSheet.id == sheet_id, CycleCountSheet.tenant_id == tenant_id)
            .options(selectinload(CycleCountSheet.lines))
        )
        res = await db.execute(query)
        sheet = res.scalar_one_or_none()

        if not sheet:
            raise EntityNotFoundError("Cycle count sheet not found.")

        if sheet.status == CycleCountStatus.APPROVED.value:
            raise BusinessRuleViolationError("Sheet is already approved and adjusted.")

        for line in sheet.lines:
            if line.variance_quantity > 0:
                # Positive adjustment
                mov_payload = StockMovementCreate(
                    movement_type=MovementType.ADJUSTMENT_POSITIVE,
                    movement_date=sheet.count_date,
                    target_warehouse_id=sheet.warehouse_id,
                    reference=sheet.sheet_number,
                    remarks=f"Cycle Count Positive Variance Adjustment ({sheet.sheet_number})",
                    lines=[
                        StockMovementLineCreate(
                            item_id=line.item_id,
                            target_location_id=line.location_id,
                            lot_id=line.lot_id,
                            quantity=line.variance_quantity,
                            unit_cost=line.unit_cost
                        )
                    ]
                )
                await StockMovementService.execute_movement(db, tenant_id, mov_payload, user_id)

            elif line.variance_quantity < 0:
                # Negative adjustment
                abs_qty = abs(line.variance_quantity)
                mov_payload = StockMovementCreate(
                    movement_type=MovementType.ADJUSTMENT_NEGATIVE,
                    movement_date=sheet.count_date,
                    source_warehouse_id=sheet.warehouse_id,
                    reference=sheet.sheet_number,
                    remarks=f"Cycle Count Negative Variance Adjustment ({sheet.sheet_number})",
                    lines=[
                        StockMovementLineCreate(
                            item_id=line.item_id,
                            source_location_id=line.location_id,
                            lot_id=line.lot_id,
                            quantity=abs_qty,
                            unit_cost=line.unit_cost
                        )
                    ]
                )
                await StockMovementService.execute_movement(db, tenant_id, mov_payload, user_id)

        sheet.status = CycleCountStatus.APPROVED.value
        await db.commit()
        await db.refresh(sheet)
        return sheet
