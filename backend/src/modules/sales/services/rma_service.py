"""
NexERP Return Material Authorization (RMA) & Customer Claims Lifecycle Engine.
Manages customer warranty claims, quarantine returns intake, disposition decisions (Restock, Rework, Scrap),
restocking fee deductions, and AR Credit Memo issuance.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.accounts_receivable.models import SalesInvoice, SalesInvoiceLine, Customer
from backend.src.modules.accounts_receivable.schemas import SalesInvoiceCreate, SalesInvoiceLineCreate
from backend.src.modules.accounts_receivable.services.sales_invoice_service import SalesInvoiceService


class RMAService:
    """
    Customer Returns Management & Credit Memo Engine.
    """

    @classmethod
    def calculate_credit_memo_amount(
        cls,
        returned_quantity: Decimal,
        original_unit_price: Decimal,
        restocking_fee_percent: Decimal = Decimal("15.0"),
        is_warranty_defect: bool = False
    ) -> Dict:
        """
        Compute net credit memo refund amount, waiving restocking fee if return is due to manufacturing defect.
        """
        gross_return_val = (returned_quantity * original_unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if is_warranty_defect:
            restock_fee = Decimal("0.0")
        else:
            restock_fee = (gross_return_val * (restocking_fee_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        net_credit_amount = gross_return_val - restock_fee

        return {
            "returned_quantity": float(returned_quantity),
            "original_unit_price": float(original_unit_price),
            "gross_return_value": float(gross_return_val),
            "restocking_fee_percent": float(restocking_fee_percent) if not is_warranty_defect else 0.0,
            "restocking_fee_amount": float(restock_fee),
            "net_credit_memo_amount": float(net_credit_amount),
            "is_warranty_defect": is_warranty_defect
        }
