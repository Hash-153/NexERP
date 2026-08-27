"""
GHG Protocol Emissions Calculation Service.
Converts energy and fuel activity data into metric tons CO2 equivalent.
"""
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.audit import AuditService
from ..models import FacilityEnergyEmissionLog, SupplierESGAudit
from ..schemas import EmissionLogCreate, SupplierESGAuditCreate

class GHGEmissionsCalculatorService:
    @staticmethod
    async def log_emission_activity(
        session: AsyncSession,
        payload: EmissionLogCreate,
        tenant_id: str,
        actor_id: str
    ) -> FacilityEnergyEmissionLog:
        # Total kg = quantity * factor; Metric tons = total kg / 1000
        total_kg = payload.consumed_quantity * payload.emission_factor_kg_co2e
        metric_tons = (total_kg / Decimal("1000.0")).quantize(Decimal("0.0001"))

        record = FacilityEnergyEmissionLog(
            tenant_id=tenant_id,
            facility_id=payload.facility_id,
            facility_name=payload.facility_name,
            reporting_period=payload.reporting_period,
            scope=payload.scope,
            energy_type=payload.energy_type,
            consumed_quantity=payload.consumed_quantity,
            unit_of_measure=payload.unit_of_measure,
            emission_factor_kg_co2e=payload.emission_factor_kg_co2e,
            calculated_metric_tons_co2e=metric_tons
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="LOG_GHG_EMISSION",
            entity_type="FacilityEnergyEmissionLog",
            entity_id=record.id,
            description=f"Calculated {metric_tons} tCO2e for {payload.facility_name} ({payload.reporting_period})"
        )
        return record

    @staticmethod
    async def get_period_summary(
        session: AsyncSession,
        period: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        stmt = select(FacilityEnergyEmissionLog).where(
            FacilityEnergyEmissionLog.reporting_period == period,
            FacilityEnergyEmissionLog.tenant_id == tenant_id
        )
        res = await session.execute(stmt)
        logs = res.scalars().all()

        scope1 = sum(l.calculated_metric_tons_co2e for l in logs if "SCOPE_1" in l.scope)
        scope2 = sum(l.calculated_metric_tons_co2e for l in logs if "SCOPE_2" in l.scope)
        scope3 = sum(l.calculated_metric_tons_co2e for l in logs if "SCOPE_3" in l.scope)

        return {
            "reporting_period": period,
            "total_metric_tons_co2e": float(scope1 + scope2 + scope3),
            "scope_1_direct": float(scope1),
            "scope_2_indirect": float(scope2),
            "scope_3_value_chain": float(scope3),
            "logs_count": len(logs)
        }
