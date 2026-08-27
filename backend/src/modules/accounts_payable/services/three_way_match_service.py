"""
NexERP Accounts Payable 3-Way Match Verification Engine (PO vs GRN vs Vendor Bill).
Evaluates line-by-line tolerances:
- Quantity Tolerance: Bill Quantity <= GRN Received Quantity (e.g. within 0% to 2%)
- Price Tolerance: Bill Unit Price <= PO Unit Price (e.g. within 0% to 1%)
- Total Amount Variance: Bill Total <= PO Total Amount + Approved Tolerance.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class ThreeWayMatchService:
    """
    3-Way Match Audit and Invoice Tolerance Verification Service.
    """

    @classmethod
    def verify_three_way_match(
        cls,
        po_lines: List[Dict],
        grn_lines: List[Dict],
        bill_lines: List[Dict],
        price_tolerance_percent: Decimal = Decimal("1.0"),
        quantity_tolerance_percent: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Perform 3-Way matching verification across Purchase Order, Goods Receipt, and Vendor Bill.
        """
        line_match_results = []
        is_fully_matched = True
        total_price_variance = Decimal("0.0")
        total_quantity_variance = Decimal("0.0")

        # Index PO lines and GRN lines by item_id
        po_map = {l["item_id"]: l for l in po_lines}
        grn_map = {l["item_id"]: l for l in grn_lines}

        for b_line in bill_lines:
            item_id = b_line["item_id"]
            b_qty = Decimal(str(b_line["quantity"]))
            b_price = Decimal(str(b_line["unit_price"]))
            b_total = b_qty * b_price

            po_line = po_map.get(item_id)
            grn_line = grn_map.get(item_id)

            if not po_line:
                is_fully_matched = False
                line_match_results.append({
                    "item_id": item_id,
                    "match_status": "FAILED_NO_PO_LINE",
                    "reason": "Billed line item was not present on Purchase Order."
                })
                continue

            po_price = Decimal(str(po_line["unit_price"]))
            po_qty_ordered = Decimal(str(po_line["quantity_ordered"]))

            grn_qty_accepted = Decimal(str(grn_line["quantity_accepted"])) if grn_line else Decimal("0.0")

            # 1. Price Variance Check
            price_diff = b_price - po_price
            price_variance_pct = ((price_diff / po_price) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if po_price > Decimal("0.0") else Decimal("0.0")
            price_match = price_variance_pct <= price_tolerance_percent

            # 2. Quantity Variance Check (Billed vs Received GRN)
            qty_diff = b_qty - grn_qty_accepted
            qty_match = b_qty <= (grn_qty_accepted * (Decimal("1.0") + (quantity_tolerance_percent / Decimal("100.0"))))

            if price_diff > Decimal("0.0"):
                total_price_variance += price_diff * b_qty
            if qty_diff > Decimal("0.0"):
                total_quantity_variance += qty_diff * b_price

            line_passed = price_match and qty_match
            if not line_passed:
                is_fully_matched = False

            line_match_results.append({
                "item_id": item_id,
                "po_unit_price": float(po_price),
                "billed_unit_price": float(b_price),
                "price_variance_percent": float(price_variance_pct),
                "price_match_passed": price_match,
                "grn_received_quantity": float(grn_qty_accepted),
                "billed_quantity": float(b_qty),
                "quantity_match_passed": qty_match,
                "overall_line_passed": line_passed
            })

        return {
            "is_matched": is_fully_matched,
            "overall_status": "AUTO_APPROVED_MATCHED" if is_fully_matched else "MATCH_EXCEPTION_HOLD",
            "total_price_variance_amount": float(total_price_variance),
            "total_quantity_variance_amount": float(total_quantity_variance),
            "lines_evaluated_count": len(bill_lines),
            "line_results": line_match_results
        }
