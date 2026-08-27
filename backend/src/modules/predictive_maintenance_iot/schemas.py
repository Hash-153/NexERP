"""
IoT Predictive Maintenance Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

class TelemetryIngestPayload(BaseModel):
    sensor_id_code: str
    vibration_velocity_rms_mm_s: Decimal
    temperature_c: Decimal
    motor_amperage: Decimal
