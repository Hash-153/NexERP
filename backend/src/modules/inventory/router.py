"""
NexERP Inventory, Multi-Bin Warehouse & Stock Valuation REST API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.inventory.models import (
    Item,
    ItemCategory,
    UnitOfMeasure,
    Warehouse,
    StockItemBalance,
    StockValuationLayer,
    StockMovement,
    CycleCountSheet
)
from backend.src.modules.inventory.schemas import (
    UOMCreate,
    UOMResponse,
    ItemCategoryCreate,
    ItemCategoryResponse,
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    WarehouseCreate,
    WarehouseLocationCreate,
    WarehouseLocationResponse,
    WarehouseResponse,
    StockMovementCreate,
    StockMovementResponse,
    StockBalanceResponse,
    ValuationLayerResponse,
    CycleCountSheetCreate,
    CycleCountSheetResponse
)
from backend.src.modules.inventory.services import (
    ItemService,
    WarehouseService,
    StockMovementService,
    CycleCountService
)

router = APIRouter(prefix="/inventory", tags=["Inventory & Warehouse Management (WMS)"])


# ==============================================================================
# Units of Measure & Categories
# ==============================================================================

@router.get("/uoms", response_model=List[UOMResponse])
async def list_uoms(
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all units of measure."""
    return await ItemService.list_uoms(db)


@router.post("/uoms", response_model=UOMResponse, status_code=status.HTTP_201_CREATED)
async def create_uom(
    payload: UOMCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new unit of measure."""
    return await ItemService.create_uom(db, current_user.tenant_id, payload)


@router.get("/categories", response_model=List[ItemCategoryResponse])
async def list_item_categories(
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List item categories and assigned valuation methods."""
    return await ItemService.list_categories(db, current_user.tenant_id)


@router.post("/categories", response_model=ItemCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_item_category(
    payload: ItemCategoryCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new item category."""
    return await ItemService.create_category(db, current_user.tenant_id, payload)


# ==============================================================================
# Item Master Catalog
# ==============================================================================

@router.get("/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List items with moving average costs and stock policies."""
    return await ItemService.list_items(db, current_user.tenant_id, skip=skip, limit=limit)


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new item master record."""
    return await ItemService.create_item(db, current_user.tenant_id, payload)


# ==============================================================================
# Warehouses & Locations
# ==============================================================================

@router.get("/warehouses", response_model=List[WarehouseResponse])
async def list_warehouses(
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List warehouses and bin location structures."""
    return await WarehouseService.list_warehouses(db, current_user.tenant_id)


@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a physical plant or distribution center."""
    return await WarehouseService.create_warehouse(db, current_user.tenant_id, payload)


@router.post("/warehouses/{warehouse_id}/locations", response_model=WarehouseLocationResponse, status_code=status.HTTP_201_CREATED)
async def add_location(
    warehouse_id: str,
    payload: WarehouseLocationCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Add a specific coordinate bin to warehouse."""
    return await WarehouseService.add_location_to_warehouse(db, current_user.tenant_id, warehouse_id, payload)


# ==============================================================================
# Stock Movements & Transactions
# ==============================================================================

@router.get("/movements", response_model=List[StockMovementResponse])
async def list_stock_movements(
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(RequirePermission("inventory:movements:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """List inventory movements and receipts."""
    query = (
        select(StockMovement)
        .where(StockMovement.tenant_id == current_user.tenant_id, StockMovement.is_deleted == False)
        .options(selectinload(StockMovement.lines))
        .order_by(StockMovement.movement_date.desc(), StockMovement.movement_number.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/movements", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def execute_stock_movement(
    payload: StockMovementCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:movements:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute stock movement (Receipt, Issue, Transfer, Adjustment) and update FIFO layers."""
    return await StockMovementService.execute_movement(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# Stock Balances & Valuation Layers
# ==============================================================================

@router.get("/balances", response_model=List[StockBalanceResponse])
async def list_stock_balances(
    item_id: Optional[str] = None,
    warehouse_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("inventory:items:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Query live stock levels by item, warehouse, and location."""
    query = select(StockItemBalance).where(StockItemBalance.tenant_id == current_user.tenant_id)
    if item_id:
        query = query.where(StockItemBalance.item_id == item_id)
    if warehouse_id:
        query = query.where(StockItemBalance.warehouse_id == warehouse_id)

    res = await db.execute(query)
    return list(res.scalars().all())


@router.get("/valuation-layers", response_model=List[ValuationLayerResponse])
async def list_valuation_layers(
    item_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("inventory:valuation:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Inspect active FIFO cost queue layers."""
    query = select(StockValuationLayer).where(
        StockValuationLayer.tenant_id == current_user.tenant_id,
        StockValuationLayer.remaining_quantity > 0
    ).order_by(StockValuationLayer.receipt_date.asc())
    if item_id:
        query = query.where(StockValuationLayer.item_id == item_id)

    res = await db.execute(query)
    return list(res.scalars().all())


# ==============================================================================
# Physical Cycle Counting
# ==============================================================================

@router.get("/cycle-counts", response_model=List[CycleCountSheetResponse])
async def list_cycle_count_sheets(
    current_user: CurrentUser = Depends(RequirePermission("inventory:cycle_count:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List physical inventory audit sheets."""
    query = (
        select(CycleCountSheet)
        .where(CycleCountSheet.tenant_id == current_user.tenant_id, CycleCountSheet.is_deleted == False)
        .options(selectinload(CycleCountSheet.lines))
        .order_by(CycleCountSheet.count_date.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/cycle-counts", response_model=CycleCountSheetResponse, status_code=status.HTTP_201_CREATED)
async def create_cycle_count_sheet(
    payload: CycleCountSheetCreate,
    current_user: CurrentUser = Depends(RequirePermission("inventory:cycle_count:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create physical count audit sheet."""
    return await CycleCountService.create_count_sheet(db, current_user.tenant_id, payload, current_user.id)


@router.post("/cycle-counts/{sheet_id}/approve", response_model=CycleCountSheetResponse)
async def approve_cycle_count_sheet(
    sheet_id: str,
    current_user: CurrentUser = Depends(RequirePermission("inventory:cycle_count:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Approve cycle count sheet and post automatic inventory reconciliation adjustments."""
    return await CycleCountService.approve_and_adjust_sheet(db, current_user.tenant_id, sheet_id, current_user.id)
