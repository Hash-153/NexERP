"""
NexERP Strategic Sourcing & Request for Quotation (RFQ) Engine.
Handles e-Sourcing sealed bid collection, multi-criteria vendor scoring (Total Cost of Ownership,
delivery lead times, ISO certifications, payment terms), and automated PO conversion.
"""

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.procurement.models import PurchaseOrder, PurchaseOrderLine
from backend.src.modules.accounts_payable.models import Vendor
from backend.src.modules.procurement.schemas import PurchaseOrderCreate, PurchaseOrderLineCreate
from backend.src.modules.procurement.services.purchase_order_service import PurchaseOrderService


class RFQAuctionService:
    """
    Strategic e-Sourcing and RFQ competitive bidding evaluation engine.
    """

    @classmethod
    def evaluate_vendor_bids(
        cls,
        bids: List[Dict],
        price_weight: Decimal = Decimal("0.50"),
        lead_time_weight: Decimal = Decimal("0.30"),
        quality_score_weight: Decimal = Decimal("0.20")
    ) -> List[Dict]:
        """
        Multi-attribute decision matrix (MADM) ranking supplier bids using normalized weighted scores.
        """
        if not bids:
            return []

        # Find min price and min lead time for normalization
        valid_prices = [Decimal(str(b["bid_unit_price"])) for b in bids if Decimal(str(b["bid_unit_price"])) > Decimal("0.0")]
        valid_leads = [Decimal(str(b["lead_time_days"])) for b in bids if Decimal(str(b["lead_time_days"])) > Decimal("0.0")]

        if not valid_prices or not valid_leads:
            return bids

        min_price = min(valid_prices)
        min_lead = min(valid_leads)

        scored_bids = []

        for b in bids:
            price = Decimal(str(b["bid_unit_price"]))
            lead = Decimal(str(b["lead_time_days"]))
            quality = Decimal(str(b.get("historical_quality_rating", 85.0)))

            # Normalized Scores (0 to 100)
            # Lower price -> higher score: (min_price / price) * 100
            score_price = (min_price / price) * Decimal("100.0") if price > Decimal("0.0") else Decimal("0.0")
            # Lower lead time -> higher score: (min_lead / lead) * 100
            score_lead = (min_lead / lead) * Decimal("100.0") if lead > Decimal("0.0") else Decimal("0.0")
            score_quality = min(Decimal("100.0"), quality)

            composite_score = (
                (score_price * price_weight) +
                (score_lead * lead_time_weight) +
                (score_quality * quality_score_weight)
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            scored_bids.append({
                "vendor_id": b["vendor_id"],
                "vendor_name": b.get("vendor_name", "Supplier"),
                "bid_unit_price": float(price),
                "lead_time_days": int(lead),
                "quality_rating": float(quality),
                "normalized_price_score": float(score_price.quantize(Decimal("0.01"))),
                "normalized_lead_time_score": float(score_lead.quantize(Decimal("0.01"))),
                "composite_score": float(composite_score),
                "is_awarded": False
            })

        # Rank descending
        scored_bids.sort(key=lambda x: x["composite_score"], reverse=True)
        if scored_bids:
            scored_bids[0]["is_awarded"] = True

        return scored_bids

    @classmethod
    async def award_rfq_and_generate_purchase_order(
        cls,
        db: AsyncSession,
        tenant_id: str,
        awarded_bid: Dict,
        rfq_reference: str,
        warehouse_id: str,
        item_id: str,
        quantity: Decimal,
        user_id: str = "system"
    ) -> PurchaseOrder:
        """
        Convert awarded winning supplier quote directly into an official Purchase Order contract.
        """
        po_payload = PurchaseOrderCreate(
            vendor_id=awarded_bid["vendor_id"],
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=awarded_bid.get("lead_time_days", 14)),
            warehouse_id=warehouse_id,
            currency="USD",
            reference=f"RFQ-AWARD:{rfq_reference}",
            notes=f"Awarded via RFQ competitive tender. Composite evaluation score: {awarded_bid.get('composite_score', 100.0)}%",
            lines=[
                PurchaseOrderLineCreate(
                    item_id=item_id,
                    quantity=quantity,
                    unit_price=Decimal(str(awarded_bid["bid_unit_price"])),
                    tax_rate=Decimal("0.0"),
                    expected_delivery_date=date.today() + timedelta(days=awarded_bid.get("lead_time_days", 14))
                )
            ]
        )

        po = await PurchaseOrderService.create_purchase_order(db, tenant_id, po_payload, user_id)
        return po
