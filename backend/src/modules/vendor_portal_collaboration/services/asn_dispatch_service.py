"""
Advance Shipping Notice (ASN) & Electronic Invoicing Service.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.audit import AuditService
from ..models import AdvanceShippingNoticeASN, VendorPortalInvoiceSubmission
from ..schemas import ASNSubmissionCreate, VendorInvoiceSubmitRequest

class ASNDispatchService:
    @staticmethod
    async def submit_asn(
        session: AsyncSession,
        payload: ASNSubmissionCreate,
        tenant_id: str,
        actor_id: str
    ) -> AdvanceShippingNoticeASN:
        asn = AdvanceShippingNoticeASN(
            tenant_id=tenant_id,
            vendor_id=payload.vendor_id,
            purchase_order_id=payload.purchase_order_id,
            asn_number=payload.asn_number,
            sscc_barcode=payload.sscc_barcode,
            status="TRANSMITTED",
            shipped_date=payload.shipped_date,
            estimated_dock_arrival=payload.estimated_dock_arrival,
            carrier_tracking_number=payload.carrier_tracking_number,
            total_cartons=payload.total_cartons,
            total_shipped_qty=payload.total_shipped_qty
        )
        session.add(asn)
        await session.commit()
        await session.refresh(asn)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="SUBMIT_ASN",
            entity_type="AdvanceShippingNoticeASN",
            entity_id=asn.id,
            description=f"Submitted ASN #{payload.asn_number} with SSCC {payload.sscc_barcode}"
        )
        return asn
