"""
Asset Capitalization, Impairment & Physical Audit Service.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.core.audit import AuditService
from ..models import FixedAssetMaster, AssetPhysicalAudit
from ..schemas import FixedAssetMasterCreate, PhysicalAuditScan

class AssetLifecycleService:
    @staticmethod
    async def create_asset(
        session: AsyncSession,
        payload: FixedAssetMasterCreate,
        tenant_id: str,
        actor_id: str
    ) -> FixedAssetMaster:
        asset = FixedAssetMaster(
            tenant_id=tenant_id,
            asset_tag=payload.asset_tag,
            serial_number=payload.serial_number,
            name=payload.name,
            description=payload.description,
            category=payload.category,
            status="ACTIVE_IN_SERVICE",
            acquisition_date=payload.acquisition_date,
            in_service_date=payload.in_service_date,
            original_acquisition_cost=payload.original_acquisition_cost,
            salvage_scrap_value=payload.salvage_scrap_value,
            useful_life_months=payload.useful_life_months,
            current_net_book_value=payload.original_acquisition_cost,
            accumulated_depreciation=Decimal("0.0"),
            location_facility=payload.location_facility,
            cost_center_code=payload.cost_center_code,
            gl_asset_account_id=payload.gl_asset_account_id,
            gl_depreciation_account_id=payload.gl_depreciation_account_id,
            gl_expense_account_id=payload.gl_expense_account_id
        )
        session.add(asset)
        await session.commit()
        await session.refresh(asset)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_FIXED_ASSET",
            entity_type="FixedAssetMaster",
            entity_id=asset.id,
            description=f"Created asset tag {payload.asset_tag} ({payload.name}) for ${payload.original_acquisition_cost}"
        )
        return asset

    @staticmethod
    async def record_physical_audit(
        session: AsyncSession,
        payload: PhysicalAuditScan,
        tenant_id: str,
        actor_id: str
    ) -> AssetPhysicalAudit:
        stmt = select(FixedAssetMaster).where(
            FixedAssetMaster.id == payload.asset_id,
            FixedAssetMaster.tenant_id == tenant_id,
            FixedAssetMaster.is_deleted == False
        )
        result = await session.execute(stmt)
        asset = result.scalar_one_or_none()
        if not asset:
            raise EntityNotFoundError("Asset not found.")

        is_discrepancy = (asset.location_facility != payload.detected_location)
        audit_rec = AssetPhysicalAudit(
            tenant_id=tenant_id,
            asset_id=payload.asset_id,
            audit_batch_code=payload.audit_batch_code,
            scanned_at=datetime.now(timezone.utc),
            scanned_by_user_id=actor_id,
            detected_location=payload.detected_location,
            condition_rating=payload.condition_rating,
            is_location_discrepancy=is_discrepancy,
            notes=payload.notes
        )
        session.add(audit_rec)
        await session.commit()
        await session.refresh(audit_rec)
        return audit_rec
