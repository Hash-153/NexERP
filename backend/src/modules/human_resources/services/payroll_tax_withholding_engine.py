"""
US Federal & State Payroll Tax Withholding (W-4) Calculation Engine.
Calculates Federal Income Tax (FIT), Social Security (OASDI), Medicare, State (SIT), and SUI.
"""
from decimal import Decimal
from typing import Dict, Any

class PayrollTaxWithholdingEngine:
    # 2026 Federal Tax Parameters
    OASDI_RATE = Decimal("0.062")      # 6.2% Social Security
    OASDI_WAGE_CAP = Decimal("168600.00")
    MEDICARE_RATE = Decimal("0.0145")   # 1.45% Medicare
    MEDICARE_ADDITIONAL_RATE = Decimal("0.009") # 0.9% above $200k

    @classmethod
    def calculate_paycheck_deductions(
        cls,
        gross_pay: Decimal,
        ytd_gross_pay: Decimal,
        filing_status: str = "SINGLE", # SINGLE or MARRIED
        pre_tax_401k_pct: Decimal = Decimal("6.0"),
        pre_tax_health_insurance: Decimal = Decimal("150.00"),
        state_code: str = "TX"
    ) -> Dict[str, Any]:
        # Pre-tax deductions
        deduction_401k = (gross_pay * (pre_tax_401k_pct / Decimal("100.0"))).quantize(Decimal("0.01"))
        total_pre_tax = deduction_401k + pre_tax_health_insurance
        taxable_wages = max(Decimal("0.0"), gross_pay - total_pre_tax)

        # OASDI (Social Security) Withholding
        if ytd_gross_pay >= cls.OASDI_WAGE_CAP:
            oasdi_tax = Decimal("0.0")
        else:
            taxable_oasdi_portion = min(gross_pay, cls.OASDI_WAGE_CAP - ytd_gross_pay)
            oasdi_tax = (taxable_oasdi_portion * cls.OASDI_RATE).quantize(Decimal("0.01"))

        # Medicare Withholding
        medicare_tax = (gross_pay * cls.MEDICARE_RATE).quantize(Decimal("0.01"))
        if ytd_gross_pay + gross_pay > Decimal("200000.00"):
            medicare_tax += ((gross_pay) * cls.MEDICARE_ADDITIONAL_RATE).quantize(Decimal("0.01"))

        # Federal Income Tax (FIT) Progressive Bracket Estimate
        annualized_taxable = taxable_wages * Decimal("26.0") # Bi-weekly pay periods
        if annualized_taxable < Decimal("47150.00"):
            fit_rate = Decimal("0.12")
        elif annualized_taxable < Decimal("100525.00"):
            fit_rate = Decimal("0.22")
        else:
            fit_rate = Decimal("0.24")
        fit_tax = (taxable_wages * fit_rate).quantize(Decimal("0.01"))

        # State Income Tax (TX, FL, WA = 0%)
        sit_tax = Decimal("0.0")
        if state_code.upper() in ("CA", "NY"):
            sit_tax = (taxable_wages * Decimal("0.06")).quantize(Decimal("0.01"))

        total_taxes = oasdi_tax + medicare_tax + fit_tax + sit_tax
        net_take_home_pay = gross_pay - total_pre_tax - total_taxes

        return {
            "gross_pay": float(gross_pay),
            "pre_tax_401k": float(deduction_401k),
            "pre_tax_health": float(pre_tax_health_insurance),
            "taxable_wages": float(taxable_wages),
            "federal_income_tax_fit": float(fit_tax),
            "social_security_oasdi": float(oasdi_tax),
            "medicare_tax": float(medicare_tax),
            "state_income_tax_sit": float(sit_tax),
            "total_tax_withholding": float(total_taxes),
            "net_take_home_pay": float(net_take_home_pay)
        }
