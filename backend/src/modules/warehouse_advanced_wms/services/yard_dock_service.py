"""
Yard Management & Dock Door Appointment Scheduling Service.
"""
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from ..models import YardDockDoor

class YardDockService:
    @staticmethod
    async def assign_trailer_to_dock(
        session: AsyncSession,
        door_number: str,
        trailer_plate: str,
        carrier_name: str,
        tenant_id: str
    ) -> YardDockDoor:
        stmt = select(YardDockDoor).where(
            YardDockDoor.door_number == door_number,
            YardDockDoor.tenant_id == tenant_id
        )
        result = await session.execute(stmt)
        door = result.scalar_one_or_none()
        if not door:
            door = YardDockDoor(
                tenant_id=tenant_id,
                door_number=door_number,
                door_type="CROSS_DOCK"
            )
            session.add(door)

        door.current_trailer_plate = trailer_plate
        door.current_carrier_name = carrier_name
        door.status = "TRUCK_ARRIVED"
        door.scheduled_arrival = datetime.utcnow()

        await session.commit()
        await session.refresh(door)
        return door
