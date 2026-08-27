"""
Audit & Forensic Compliance REST API Router.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .schemas import ControlRuleCreate, AnomalyDetectionRequest
from .services import ForensicAnomalyDetectorService

router = APIRouter(prefix="/audit-compliance", tags=["Audit & Forensic Compliance"])

@router.post("/evaluate-risk")
async def evaluate_journal_risk(
    payload: AnomalyDetectionRequest,
    user: CurrentUser = Depends(get_current_user)
):
    return ForensicAnomalyDetectorService.evaluate_journal_risk(
        journal_number="JV-TEST-001",
        amount=payload.posted_amount,
        is_weekend_posted=payload.is_weekend,
        is_manual_entry=payload.is_manual_entry,
        is_round_dollar_amount=payload.is_round_number,
        user_created_by=user.email
    )
