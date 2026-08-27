"""
Freight Rating & Dimensional Weight Calculation Service.
Calculates IATA standard volumetric weights and dynamic fuel surcharges.
"""
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.audit import AuditService
from ..models import ShipmentDispatch
from ..schemas import ShipmentDispatchCreate

class FreightRatingEngineService:
    @staticmethod
    def calculate_chargeable_weight(gross_kg: Decimal, l_cm: Decimal, w_cm: Decimal, h_cm: Decimal) -> Decimal:
        # Standard volumetric divisor: 5000 cm3/kg for Road, 6000 for Air
        volume_cm3 = l_cm * w_cm * h_cm
        dim_weight_kg = (volume_cm3 / Decimal("5000.0")).quantize(Decimal("0.01"))
        return max(gross_kg, dim_weight_kg), dim_weight_kg

    @staticmethod
    async def create_rated_dispatch(
        session: AsyncSession,
        payload: ShipmentDispatchCreate,
        tenant_id: str,
        actor_id: str
    ) -> ShipmentDispatch:
        chargeable_wt, dim_wt = FreightRatingEngineService.calculate_chargeable_weight(
            payload.gross_weight_kg, payload.length_cm, payload.width_cm, payload.height_cm
        )

        quoted_freight = chargeable_wt * payload.base_rate_per_kg
        fuel_surcharge = quoted_freight * Decimal("0.145")  # 14.5% standard diesel index
        total_cost = quoted_freight + fuel_surcharge

        dispatch = ShipmentDispatch(
            tenant_id=tenant_id,
            carrier_id=payload.carrier_id,
            tracking_bol_number=payload.tracking_bol_number,
            transport_mode=payload.transport_mode,
            status="BOOKED",
            origin_address=payload.origin_address,
            destination_address=payload.destination_address,
            scheduled_pickup=payload.scheduled_pickup,
            estimated_delivery=payload.estimated_delivery,
            total_pallets=payload.total_pallets,
            gross_weight_kg=payload.gross_weight_kg,
            dimensional_weight_kg=dim_wt,
            chargeable_weight_kg=chargeable_wt,
            quoted_freight_charge=quoted_freight,
            fuel_surcharge=fuel_surcharge,
            accessorial_charges=Decimal("0.0"),
            total_cost=total_cost
        )
        session.add(dispatch)
        await session.commit()
        await session.refresh(dispatch)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_DISPATCH",
            entity_type="ShipmentDispatch",
            entity_id=dispatch.id,
            description=f"Created dispatch BOL {payload.tracking_bol_number} rated at ${total_cost}"
        )
        return dispatch
