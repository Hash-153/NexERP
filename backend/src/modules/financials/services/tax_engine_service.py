"""
NexERP Multi-Jurisdiction Indirect Tax Engine.
Supports US Sales & Use Tax, EU/UK Value Added Tax (VAT) with reverse-charge rules,
Canadian GST/PST/HST, Indian GST, and automated periodic tax settlement returns.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.financials.models import TaxRate, TaxCategory, Account


class TaxEngineService:
    """
    Automates complex multi-tier tax computations for AP Bills and AR Invoices.
    """

    @classmethod
    def calculate_line_taxes(
        cls,
        net_amount: Decimal,
        tax_rates: List[Dict],
        is_compound: bool = False,
        is_inclusive: bool = False
    ) -> Dict:
        """
        Calculate total tax breakdown across multiple rates (e.g. State 4% + City 4.5% + County 0.375%).
        Handles standard exclusive, inclusive, and cascading compound tax rules.
        """
        if net_amount <= Decimal("0.0") or not tax_rates:
            return {
                "base_amount": float(net_amount),
                "total_tax_amount": 0.0,
                "gross_amount": float(net_amount),
                "tax_breakdown": []
            }

        total_tax = Decimal("0.0")
        breakdown = []
        running_base = net_amount

        if is_inclusive:
            # Calculate back out from total gross
            combined_rate = sum(Decimal(str(r["rate_percent"])) for r in tax_rates)
            divisor = Decimal("1.0") + (combined_rate / Decimal("100.0"))
            calculated_net = (net_amount / divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            calculated_total_tax = net_amount - calculated_net

            for r in tax_rates:
                pct = Decimal(str(r["rate_percent"]))
                portion = (calculated_total_tax * (pct / combined_rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                breakdown.append({
                    "tax_code": r.get("code", "TAX"),
                    "rate_percent": float(pct),
                    "tax_amount": float(portion),
                    "account_id": r.get("account_id")
                })
            return {
                "base_amount": float(calculated_net),
                "total_tax_amount": float(calculated_total_tax),
                "gross_amount": float(net_amount),
                "tax_breakdown": breakdown
            }

        # Standard Exclusive & Compound
        for r in tax_rates:
            pct = Decimal(str(r["rate_percent"]))
            if is_compound:
                tax_amt = (running_base * (pct / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                running_base += tax_amt
            else:
                tax_amt = (net_amount * (pct / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            total_tax += tax_amt
            breakdown.append({
                "tax_code": r.get("code", "TAX"),
                "rate_percent": float(pct),
                "tax_amount": float(tax_amt),
                "account_id": r.get("account_id")
            })

        gross_amt = net_amount + total_tax
        return {
            "base_amount": float(net_amount),
            "total_tax_amount": float(total_tax),
            "gross_amount": float(gross_amt),
            "tax_breakdown": breakdown
        }

    @classmethod
    async def generate_periodic_tax_return_summary(
        cls,
        db: AsyncSession,
        tenant_id: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Aggregate Output Tax (collected on sales) and Input Tax (paid on purchases)
        to compute net statutory tax payable or refundable to government revenue authorities.
        """
        # Fetch output tax (Sales Invoices) & input tax (Vendor Bills)
        from backend.src.modules.accounts_receivable.models import SalesInvoice
        from backend.src.modules.accounts_payable.models import VendorBill
        from backend.src.modules.financials.enums import InvoiceStatus, BillStatus

        inv_query = (
            select(SalesInvoice)
            .where(
                SalesInvoice.tenant_id == tenant_id,
                SalesInvoice.status == InvoiceStatus.POSTED.value,
                SalesInvoice.invoice_date.between(start_date, end_date)
            )
        )
        inv_res = await db.execute(inv_query)
        invoices = list(inv_res.scalars().all())

        bill_query = (
            select(VendorBill)
            .where(
                VendorBill.tenant_id == tenant_id,
                VendorBill.status == BillStatus.POSTED.value,
                VendorBill.bill_date.between(start_date, end_date)
            )
        )
        bill_res = await db.execute(bill_query)
        bills = list(bill_res.scalars().all())

        taxable_sales = sum(i.subtotal for i in invoices)
        output_tax_collected = sum(i.tax_amount for i in invoices)

        taxable_purchases = sum(b.subtotal for b in bills)
        input_tax_paid = sum(b.tax_amount for b in bills)

        net_tax_liability = (output_tax_collected - input_tax_paid).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_taxable_sales": float(taxable_sales),
            "total_output_tax_collected": float(output_tax_collected),
            "total_taxable_purchases": float(taxable_purchases),
            "total_input_tax_credit": float(input_tax_paid),
            "net_tax_payable_to_authority": float(max(Decimal("0.0"), net_tax_liability)),
            "net_tax_refund_due": float(abs(min(Decimal("0.0"), net_tax_liability))),
            "status": "PAYMENT_REQUIRED" if net_tax_liability > Decimal("0.0") else "REFUND_CLAIM"
        }
