"""
Subscription Billing REST API Router.
"""
from fastapi import APIRouter, Depends, status
from backend.src.core.dependencies import get_current_user, CurrentUser
from .schemas import SubscriptionCreate
from .services import ASC606RevenueScheduleService

router = APIRouter(prefix="/subscriptions", tags=["Subscription Billing & ASC 606"])

@router.post("/asc606/waterfall")
async def get_revenue_waterfall(
    payload: SubscriptionCreate,
    user: CurrentUser = Depends(get_current_user)
):
    return ASC606RevenueScheduleService.generate_recognition_waterfall(
        total_contract_value=payload.annual_contract_value,
        term_months=12
    )
