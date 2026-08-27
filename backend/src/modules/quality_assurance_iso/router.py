"""
Quality Assurance ISO REST API Router.
"""
from fastapi import APIRouter, Depends, status
from backend.src.core.dependencies import get_current_user, CurrentUser
from .schemas import FMEARecordCreate
from .services import FMEARiskAnalyzerService

router = APIRouter(prefix="/qa-iso", tags=["Quality Assurance & ISO Standards"])

@router.post("/fmea/calculate")
async def calculate_fmea_rpn(
    payload: FMEARecordCreate,
    user: CurrentUser = Depends(get_current_user)
):
    return FMEARiskAnalyzerService.calculate_rpn(
        severity=payload.severity,
        occurrence=payload.occurrence,
        detection=payload.detection
    )
