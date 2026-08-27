"""
Customer Real-Time Credit Exposure & Limit Breach Protection Engine.
Monitors Total Exposure = Outstanding Invoices + Unbilled Shipments + Open Sales Orders.
"""
from decimal import Decimal
from typing import Dict, Any

class CustomerCreditExposureService:
    @staticmethod
    def evaluate_credit_availability(
        customer_account_id: str,
        approved_credit_limit: Decimal,
        outstanding_ar_balance: Decimal,
        unbilled_delivered_orders: Decimal,
        open_unfulfilled_orders: Decimal,
        new_order_amount: Decimal
    ) -> Dict[str, Any]:
        current_exposure = outstanding_ar_balance + unbilled_delivered_orders + open_unfulfilled_orders
        projected_exposure = current_exposure + new_order_amount
        available_credit = approved_credit_limit - current_exposure
        projected_available = approved_credit_limit - projected_exposure

        is_breach = projected_exposure > approved_credit_limit
        overage_amount = max(Decimal("0.0"), projected_exposure - approved_credit_limit)

        return {
            "customer_account_id": customer_account_id,
            "approved_credit_limit": float(approved_credit_limit),
            "current_credit_exposure": float(current_exposure),
            "current_available_credit": float(available_credit),
            "new_order_amount": float(new_order_amount),
            "projected_total_exposure": float(projected_exposure),
            "projected_available_credit": float(projected_available),
            "is_credit_limit_breached": is_breach,
            "overage_breach_amount": float(overage_amount),
            "recommendation": "APPROVE_ORDER" if not is_breach else "PLACE_ON_CREDIT_HOLD"
        }
