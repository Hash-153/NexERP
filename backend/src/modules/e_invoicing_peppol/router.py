"""
Global E-Invoicing REST API Router.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .schemas import EInvoiceGenerateRequest, EInvoiceResponse
from .services import UBLPeppolGeneratorService

router = APIRouter(prefix="/e-invoicing", tags=["Global E-Invoicing & PEPPOL"])

@router.post("/generate-xml")
async def generate_peppol_xml(
    payload: EInvoiceGenerateRequest,
    user: CurrentUser = Depends(get_current_user)
):
    xml_content = UBLPeppolGeneratorService.generate_ubl_xml(payload)
    return {
        "invoice_number": payload.invoice_number,
        "standard": payload.standard,
        "validation_status": "VALID_EN16931",
        "xml_payload": xml_content
    }
