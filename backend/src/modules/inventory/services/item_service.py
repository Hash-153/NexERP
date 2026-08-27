"""
NexERP Item Master & Catalog Management Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.inventory.models import Item, ItemCategory, UnitOfMeasure
from backend.src.modules.inventory.schemas import ItemCreate, ItemUpdate, ItemCategoryCreate, UOMCreate


class ItemService:
    """
    Manages items, categories, and unit of measure definitions.
    """

    @classmethod
    async def create_uom(cls, db: AsyncSession, tenant_id: str, payload: UOMCreate) -> UnitOfMeasure:
        query = select(UnitOfMeasure).where(UnitOfMeasure.code == payload.code.upper().strip())
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"UOM '{payload.code}' already exists.")

        uom = UnitOfMeasure(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            category=payload.category
        )
        db.add(uom)
        await db.commit()
        await db.refresh(uom)
        return uom

    @classmethod
    async def list_uoms(cls, db: AsyncSession) -> List[UnitOfMeasure]:
        query = select(UnitOfMeasure).order_by(UnitOfMeasure.code.asc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def create_category(cls, db: AsyncSession, tenant_id: str, payload: ItemCategoryCreate) -> ItemCategory:
        query = select(ItemCategory).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.code == payload.code.upper().strip(),
            ItemCategory.is_deleted == False
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Category '{payload.code}' already exists.")

        cat = ItemCategory(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            valuation_method=payload.valuation_method.value,
            inventory_account_id=payload.inventory_account_id,
            cogs_account_id=payload.cogs_account_id,
            variance_account_id=payload.variance_account_id
        )
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return cat

    @classmethod
    async def list_categories(cls, db: AsyncSession, tenant_id: str) -> List[ItemCategory]:
        query = select(ItemCategory).where(ItemCategory.tenant_id == tenant_id, ItemCategory.is_deleted == False)
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def create_item(cls, db: AsyncSession, tenant_id: str, payload: ItemCreate) -> Item:
        query = select(Item).where(
            Item.tenant_id == tenant_id,
            Item.sku == payload.sku.upper().strip(),
            Item.is_deleted == False
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Item SKU '{payload.sku}' already exists.")

        item = Item(
            tenant_id=tenant_id,
            sku=payload.sku.upper().strip(),
            name=payload.name.strip(),
            description=payload.description,
            barcode=payload.barcode,
            category_id=payload.category_id,
            uom_id=payload.uom_id,
            item_type=payload.item_type.value,
            is_serialized=payload.is_serialized,
            is_batch_tracked=payload.is_batch_tracked,
            min_stock_level=payload.min_stock_level,
            max_stock_level=payload.max_stock_level,
            reorder_point=payload.reorder_point,
            safety_stock=payload.safety_stock,
            lead_time_days=payload.lead_time_days,
            standard_cost=payload.standard_cost,
            moving_average_cost=payload.standard_cost,
            list_price=payload.list_price
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @classmethod
    async def list_items(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Item]:
        query = (
            select(Item)
            .where(Item.tenant_id == tenant_id, Item.is_deleted == False)
            .options(
                selectinload(Item.category),
                selectinload(Item.uom)
            )
            .order_by(Item.sku.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(query)
        return list(res.scalars().all())
