"""
Customer RMA Return Dispositioning, Restocking Fee & Refund Credit Memo Engine.
"""
from decimal import Decimal
from typing import Dict, Any

class RMADispositionService:
    @staticmethod
    def evaluate_return_credit(
        original_item_price: Decimal,
        quantity: Decimal,
        return_reason: str, # DEFECTIVE_WARRANTY, BUYERS_REMORSE, WRONG_ITEM_SHIPPED
        days_since_delivery: int,
        item_condition: str = "UNOPENED_ORIGINAL_BOX"
    ) -> Dict[str, Any]:
        gross_return_val = original_item_price * quantity
        restocking_fee_pct = Decimal("0.0")
        is_warranty = False

        if return_reason == "DEFECTIVE_WARRANTY":
            restocking_fee_pct = Decimal("0.0")
            is_warranty = True
        elif return_reason == "WRONG_ITEM_SHIPPED":
            restocking_fee_pct = Decimal("0.0")
        elif return_reason == "BUYERS_REMORSE":
            if days_since_delivery > 30:
                restocking_fee_pct = Decimal("25.0")
            elif item_condition == "OPENED_RESEALABLE":
                restocking_fee_pct = Decimal("15.0")
            else:
                restocking_fee_pct = Decimal("10.0")

        fee_amount = (gross_return_val * (restocking_fee_pct / Decimal("100.0"))).quantize(Decimal("0.01"))
        net_credit_memo = gross_return_val - fee_amount

        return {
            "gross_return_value": float(gross_return_val),
            "restocking_fee_percentage": float(restocking_fee_pct),
            "restocking_fee_amount": float(fee_amount),
            "net_credit_memo_refund": float(net_credit_memo),
            "is_warranty_claim": is_warranty,
            "disposition": "RETURN_TO_STOCK_RESTOCK" if item_condition == "UNOPENED_ORIGINAL_BOX" else "INSPECTION_REFURBISH_QUEUE"
        }
