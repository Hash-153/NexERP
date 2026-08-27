"""
NexERP Lease Accounting Engine (ASC 842 / IFRS 16).
Calculates:
- Present Value of Lease Payments using Discount Rate (IBR - Incremental Borrowing Rate)
- Initial Right-of-Use (ROU) Asset Capitalization
- Monthly Lease Amortization Schedule (Interest Expense, Liability Reduction, ROU Depreciation)
- Operating Lease vs Finance / Capital Lease Classification Test.
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class LeaseAccountingService:
    """
    ASC 842 / IFRS 16 Lease Valuation & Amortization Engine.
    """

    @classmethod
    def classify_lease(
        cls,
        lease_term_months: int,
        asset_economic_life_months: int,
        present_value_payments: Decimal,
        fair_value_underlying_asset: Decimal,
        has_ownership_transfer: bool = False,
        has_purchase_option: bool = False,
        is_specialized_asset: bool = False
    ) -> str:
        """
        ASC 842 5-Criteria Classification Test (Operating vs Finance Lease).
        """
        # Criterion 1: Ownership transfer to lessee at end of term
        if has_ownership_transfer:
            return "FINANCE_LEASE"

        # Criterion 2: Lessee reasonably certain to exercise purchase option
        if has_purchase_option:
            return "FINANCE_LEASE"

        # Criterion 3: Lease term >= 75% of economic life
        term_ratio = Decimal(str(lease_term_months)) / Decimal(str(asset_economic_life_months))
        if term_ratio >= Decimal("0.75"):
            return "FINANCE_LEASE"

        # Criterion 4: PV of lease payments >= 90% of asset fair value
        pv_ratio = present_value_payments / fair_value_underlying_asset if fair_value_underlying_asset > Decimal("0.0") else Decimal("0.0")
        if pv_ratio >= Decimal("0.90"):
            return "FINANCE_LEASE"

        # Criterion 5: Specialized asset with no alternative use to lessor
        if is_specialized_asset:
            return "FINANCE_LEASE"

        return "OPERATING_LEASE"

    @classmethod
    def calculate_lease_schedule(
        cls,
        monthly_payment: Decimal,
        lease_term_months: int,
        annual_discount_rate_percent: Decimal,
        start_date: date,
        initial_direct_costs: Decimal = Decimal("0.0"),
        lease_incentives: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Generate complete ASC 842 amortization table for ROU Asset and Lease Liability.
        """
        if lease_term_months <= 0 or monthly_payment <= Decimal("0.0"):
            raise ValueError("Lease term and payment must be strictly positive.")

        monthly_rate = (annual_discount_rate_percent / Decimal("100.0")) / Decimal("12.0")

        # Present Value (PV) of annuity: PV = PMT * [(1 - (1+r)^-n) / r]
        if monthly_rate > Decimal("0.0"):
            discount_factor = (Decimal("1.0") - (Decimal("1.0") + monthly_rate) ** (-lease_term_months)) / monthly_rate
            initial_pv = (monthly_payment * discount_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            initial_pv = (monthly_payment * Decimal(str(lease_term_months))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Initial ROU Asset = Initial Liability + Initial Direct Costs - Lease Incentives
        initial_rou_asset = initial_pv + initial_direct_costs - lease_incentives
        monthly_rou_depreciation = (initial_rou_asset / Decimal(str(lease_term_months))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        schedule = []
        liability_balance = initial_pv
        rou_asset_balance = initial_rou_asset

        for month in range(1, lease_term_months + 1):
            interest_expense = (liability_balance * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            principal_reduction = monthly_payment - interest_expense
            liability_balance = max(Decimal("0.0"), liability_balance - principal_reduction)
            rou_asset_balance = max(Decimal("0.0"), rou_asset_balance - monthly_rou_depreciation)

            schedule.append({
                "period_month": month,
                "payment_amount": float(monthly_payment),
                "interest_expense": float(interest_expense),
                "liability_principal_reduction": float(principal_reduction),
                "ending_lease_liability": float(liability_balance),
                "rou_asset_depreciation": float(monthly_rou_depreciation),
                "ending_rou_asset_book_value": float(rou_asset_balance)
            })

        return {
            "initial_lease_liability": float(initial_pv),
            "initial_rou_asset": float(initial_rou_asset),
            "total_lease_payments": float(monthly_payment * Decimal(str(lease_term_months))),
            "total_interest_cost": float((monthly_payment * Decimal(str(lease_term_months))) - initial_pv),
            "monthly_discount_rate_percent": float((monthly_rate * Decimal("100.0")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)),
            "schedule": schedule
        }
