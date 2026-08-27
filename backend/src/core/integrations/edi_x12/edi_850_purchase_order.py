"""
ANSI ASC X12 Transaction Set 850 (Purchase Order) Parser.
"""
from decimal import Decimal
from typing import Dict, Any, List

class EDI850PurchaseOrderParser:
    @staticmethod
    def parse_x12_850_string(edi_text: str) -> Dict[str, Any]:
        """Parses standard X12 850 segment stream."""
        segments = [s.strip() for s in edi_text.split("~") if s.strip()]
        po_number = ""
        po_date = ""
        vendor_code = ""
        items = []

        for seg in segments:
            elements = seg.split("*")
            tag = elements[0]
            if tag == "BEG":
                # BEG*00*SA*PO100293**20260301
                if len(elements) > 3:
                    po_number = elements[3]
                if len(elements) > 5:
                    po_date = elements[5]
            elif tag == "N1" and len(elements) > 4:
                if elements[1] == "VN":
                    vendor_code = elements[4]
            elif tag == "PO1":
                # PO1*1*100*EA*24.50**VN*SKU-9948
                line_no = elements[1] if len(elements) > 1 else "1"
                qty = Decimal(elements[2]) if len(elements) > 2 else Decimal("1.0")
                unit_price = Decimal(elements[4]) if len(elements) > 4 else Decimal("0.0")
                sku = elements[7] if len(elements) > 7 else "UNKNOWN"
                items.append({
                    "line_number": int(line_no),
                    "sku": sku,
                    "quantity": float(qty),
                    "unit_price": float(unit_price),
                    "extended_total": float(qty * unit_price)
                })

        total_val = sum(Decimal(str(it["extended_total"])) for it in items)
        return {
            "transaction_set": "850",
            "purchase_order_number": po_number,
            "order_date": po_date,
            "vendor_code": vendor_code,
            "total_lines": len(items),
            "total_order_amount": float(total_val),
            "line_items": items
        }
