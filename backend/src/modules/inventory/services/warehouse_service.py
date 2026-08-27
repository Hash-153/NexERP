"""
NexERP Warehouse Topology & Multi-Bin Storage Management Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.inventory.models import Warehouse, WarehouseLocation
from backend.src.modules.inventory.schemas import WarehouseCreate, WarehouseLocationCreate


class WarehouseService:
    """
    Manages physical plants, distribution centers, and storage bins.
    """

    @classmethod
    async def create_warehouse(cls, db: AsyncSession, tenant_id: str, payload: WarehouseCreate) -> Warehouse:
        query = select(Warehouse).where(
            Warehouse.tenant_id == tenant_id,
            Warehouse.code == payload.code.upper().strip(),
            Warehouse.is_deleted == False
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Warehouse code '{payload.code}' already exists.")

        wh = Warehouse(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            address=payload.address,
            is_quarantine=payload.is_quarantine,
            is_transit=payload.is_transit
        )
        db.add(wh)
        await db.commit()
        await db.refresh(wh)
        return wh

    @classmethod
    async def add_location_to_warehouse(
        cls,
        db: AsyncSession,
        tenant_id: str,
        warehouse_id: str,
        payload: WarehouseLocationCreate
    ) -> WarehouseLocation:
        loc = WarehouseLocation(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            location_code=payload.location_code.strip(),
            zone=payload.zone,
            aisle=payload.aisle,
            rack=payload.rack,
            shelf=payload.shelf,
            bin=payload.bin,
            max_weight_capacity_kg=payload.max_weight_capacity_kg
        )
        db.add(loc)
        await db.commit()
        await db.refresh(loc)
        return loc

    @classmethod
    async def list_warehouses(cls, db: AsyncSession, tenant_id: str) -> List[Warehouse]:
        query = (
            select(Warehouse)
            .where(Warehouse.tenant_id == tenant_id, Warehouse.is_deleted == False)
            .options(selectinload(Warehouse.locations))
            .order_by(Warehouse.code.asc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
