"""
ASC 842 / IFRS 16 Lease Accounting & Amortization Engine.
Computes Right-of-Use (ROU) asset schedules, operating/finance lease liabilities, and discount rate present values.
"""
from decimal import Decimal
from typing import Dict, Any, List
from datetime import date

class LeaseAccountingASC842Engine:
    @staticmethod
    def calculate_lease_present_value(
        monthly_payment: Decimal,
        term_months: int,
        annual_discount_rate_ibr: Decimal  # Incremental Borrowing Rate (IBR)
    ) -> Decimal:
        """Present value of future lease payments discounted at monthly IBR."""
        monthly_rate = annual_discount_rate_ibr / Decimal("12.0")
        pv = Decimal("0.0")
        for m in range(1, term_months + 1):
            discount_factor = (Decimal("1.0") + monthly_rate) ** m
            pv += monthly_payment / discount_factor
        return pv.quantize(Decimal("0.01"))

    @classmethod
    def generate_amortization_schedule(
        cls,
        lease_identifier: str,
        monthly_payment: Decimal,
        term_months: int,
        annual_discount_rate: Decimal,
        lease_type: str = "OPERATING" # OPERATING or FINANCE
    ) -> Dict[str, Any]:
        initial_liability = cls.calculate_lease_present_value(monthly_payment, term_months, annual_discount_rate)
        initial_rou_asset = initial_liability  # assuming zero initial direct costs or incentives
        
        monthly_rate = annual_discount_rate / Decimal("12.0")
        monthly_straight_line_expense = (monthly_payment * Decimal(str(term_months))) / Decimal(str(term_months))
        
        schedule = []
        carrying_liability = initial_liability
        carrying_rou = initial_rou_asset
        
        for m in range(1, term_months + 1):
            interest_expense = (carrying_liability * monthly_rate).quantize(Decimal("0.01"))
            principal_reduction = monthly_payment - interest_expense
            new_liability = max(Decimal("0.0"), carrying_liability - principal_reduction)
            
            if lease_type == "OPERATING":
                # Single lease cost = straight line payment; ROU amortization = lease cost - interest
                rou_amortization = monthly_straight_line_expense - interest_expense
            else:
                # Finance lease: straight-line ROU amortization
                rou_amortization = (initial_rou_asset / Decimal(str(term_months))).quantize(Decimal("0.01"))
                
            new_rou = max(Decimal("0.0"), carrying_rou - rou_amortization)
            
            schedule.append({
                "period_month": m,
                "beginning_liability": float(carrying_liability),
                "lease_payment": float(monthly_payment),
                "interest_expense": float(interest_expense),
                "principal_reduction": float(principal_reduction),
                "ending_liability": float(new_liability),
                "beginning_rou_asset": float(carrying_rou),
                "rou_amortization": float(rou_amortization),
                "ending_rou_asset": float(new_rou)
            })
            
            carrying_liability = new_liability
            carrying_rou = new_rou
            
        return {
            "lease_identifier": lease_identifier,
            "lease_type": lease_type,
            "term_months": term_months,
            "discount_rate_ibr": float(annual_discount_rate),
            "initial_rou_asset_value": float(initial_rou_asset),
            "initial_lease_liability": float(initial_liability),
            "schedule": schedule
        }
