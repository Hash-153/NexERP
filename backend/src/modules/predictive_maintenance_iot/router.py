"""
IoT Predictive Maintenance REST API Router.
"""
from fastapi import APIRouter, Depends, status
from backend.src.core.dependencies import get_current_user, CurrentUser
from .schemas import TelemetryIngestPayload
from .services import FFTVibrationAnalyzerService

router = APIRouter(prefix="/iot-maintenance", tags=["IoT Predictive Maintenance"])

@router.post("/telemetry/analyze")
async def analyze_sensor_telemetry(
    payload: TelemetryIngestPayload,
    user: CurrentUser = Depends(get_current_user)
):
    return FFTVibrationAnalyzerService.analyze_vibration_rms(
        velocity_rms_mm_s=payload.vibration_velocity_rms_mm_s,
        temp_c=payload.temperature_c
    )
