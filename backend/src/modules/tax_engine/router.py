"""
Tax Engine REST API Router.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .schemas import TaxCalculationRequest, TaxCalculationResult
from .services import SalesTaxJurisdictionService

router = APIRouter(prefix="/tax", tags=["Tax Engine & Multi-Jurisdiction Nexus"])

@router.post("/calculate", response_model=TaxCalculationResult)
async def calculate_taxes(
    payload: TaxCalculationRequest,
    user: CurrentUser = Depends(get_current_user)
):
    res = SalesTaxJurisdictionService.calculate_us_sales_tax(
        state=payload.state_province,
        amount=payload.line_amount,
        is_exempt=payload.is_resale_exempt
    )
    return TaxCalculationResult(
        transaction_id=payload.transaction_id,
        taxable_amount=payload.line_amount,
        combined_rate=Decimal(str(res["combined_rate"])),
        state_tax_amount=Decimal(str(res["state_tax"])),
        local_tax_amount=Decimal(str(res["local_tax"])),
        total_tax_amount=Decimal(str(res["total_tax"])),
        jurisdiction_summary=res["jurisdiction"]
    )
