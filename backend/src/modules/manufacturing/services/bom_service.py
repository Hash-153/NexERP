"""
NexERP Multi-Level Bill of Materials (BOM) & Recursive Explosion Service.
Handles multi-level BOM creation, circular dependency cycle detection, phantom subassembly resolution,
and automated cost roll-up calculations.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BOMRecursionError, BusinessRuleViolationError
from backend.src.modules.manufacturing.models import BillOfMaterials, BOMLine
from backend.src.modules.manufacturing.schemas import BOMCreate
from backend.src.modules.inventory.models import Item


class BOMService:
    """
    Bill of Materials engineering and recursive explosion service.
    """

    @classmethod
    async def create_bom(cls, db: AsyncSession, tenant_id: str, payload: BOMCreate) -> BillOfMaterials:
        bom = BillOfMaterials(
            tenant_id=tenant_id,
            bom_number=payload.bom_number.strip(),
            item_id=payload.item_id,
            quantity=payload.quantity,
            uom_id=payload.uom_id,
            version=payload.version,
            is_default=payload.is_default,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to
        )
        db.add(bom)
        await db.flush()

        for line in payload.lines:
            b_line = BOMLine(
                tenant_id=tenant_id,
                bom_id=bom.id,
                item_id=line.item_id,
                quantity=line.quantity,
                uom_id=line.uom_id,
                scrap_percentage=line.scrap_percentage,
                is_phantom=line.is_phantom,
                operation_sequence_number=line.operation_sequence_number
            )
            db.add(b_line)

        # Validate no circular recursion
        await cls.detect_bom_cycles(db, tenant_id, payload)

        await db.commit()
        await db.refresh(bom)
        return bom

    @classmethod
    async def detect_bom_cycles(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: BOMCreate
    ) -> None:
        """
        DFS graph cycle detection to guarantee BOM hierarchy is a Directed Acyclic Graph (DAG).
        """
        graph: Dict[str, List[str]] = {}

        # Fetch all active BOMs
        res = await db.execute(
            select(BillOfMaterials)
            .where(BillOfMaterials.tenant_id == tenant_id, BillOfMaterials.is_default == True)
            .options(selectinload(BillOfMaterials.lines))
        )
        for b in res.scalars().all():
            graph[b.item_id] = [l.item_id for l in b.lines]

        # Add currently proposed BOM to graph
        graph[payload.item_id] = [l.item_id for l in payload.lines]

        def dfs(current_item: str, path: Set[str]) -> bool:
            if current_item in path:
                return True
            path.add(current_item)
            for child_item in graph.get(current_item, []):
                if dfs(child_item, path.copy()):
                    return True
            return False

        if dfs(payload.item_id, set()):
            raise BOMRecursionError(
                f"Circular reference detected in BOM hierarchy involving Item ID '{payload.item_id}'."
            )

    @classmethod
    async def explode_bom_multi_level(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str,
        demand_quantity: Decimal = Decimal("1.0"),
        level: int = 1
    ) -> List[Dict]:
        """
        Recursively explode multi-level BOM down to base raw materials and calculate scrap multipliers.
        """
        query = (
            select(BillOfMaterials)
            .where(
                BillOfMaterials.tenant_id == tenant_id,
                BillOfMaterials.item_id == item_id,
                BillOfMaterials.is_default == True,
                BillOfMaterials.is_deleted == False
            )
            .options(
                selectinload(BillOfMaterials.lines).selectinload(BOMLine.item)
            )
        )
        res = await db.execute(query)
        bom = res.scalar_one_or_none()

        if not bom:
            return []

        exploded_components = []

        for line in bom.lines:
            scrap_multiplier = Decimal("1.0") + (line.scrap_percentage / Decimal("100.0"))
            component_demand = (line.quantity / bom.quantity) * demand_quantity * scrap_multiplier

            exploded_components.append({
                "level": level,
                "item_id": line.item_id,
                "sku": line.item.sku,
                "name": line.item.name,
                "quantity_required": component_demand.quantize(Decimal("0.0001")),
                "scrap_percentage": float(line.scrap_percentage),
                "is_phantom": line.is_phantom,
                "standard_cost": float(line.item.standard_cost),
                "total_estimated_cost": float(component_demand * line.item.standard_cost)
            })

            # Recurse down subassembly if item is not a pure raw material
            sub_components = await cls.explode_bom_multi_level(
                db=db,
                tenant_id=tenant_id,
                item_id=line.item_id,
                demand_quantity=component_demand,
                level=level + 1
            )
            exploded_components.extend(sub_components)

        return exploded_components

    @classmethod
    async def list_boms(cls, db: AsyncSession, tenant_id: str) -> List[BillOfMaterials]:
        query = (
            select(BillOfMaterials)
            .where(BillOfMaterials.tenant_id == tenant_id, BillOfMaterials.is_deleted == False)
            .options(selectinload(BillOfMaterials.lines))
            .order_by(BillOfMaterials.created_at.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
