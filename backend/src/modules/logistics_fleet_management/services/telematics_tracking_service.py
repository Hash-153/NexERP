"""
Telematics & Geofencing Tracking Service.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import FleetTelematicsPing
from ..schemas import TelematicsPingCreate

class TelematicsTrackingService:
    @staticmethod
    async def record_telemetry(
        session: AsyncSession,
        payload: TelematicsPingCreate,
        tenant_id: str
    ) -> FleetTelematicsPing:
        ping = FleetTelematicsPing(
            tenant_id=tenant_id,
            shipment_id=payload.shipment_id,
            recorded_at=datetime.now(timezone.utc),
            latitude=payload.latitude,
            longitude=payload.longitude,
            speed_kmh=payload.speed_kmh,
            temperature_c=payload.temperature_c,
            geofence_status="INSIDE_CORRIDOR"
        )
        session.add(ping)
        await session.commit()
        await session.refresh(ping)
        return ping
