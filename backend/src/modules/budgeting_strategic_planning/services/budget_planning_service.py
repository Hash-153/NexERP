"""
Strategic Budget Planning & Zero-Based Allocation Service.
"""
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.audit import AuditService
from ..models import StrategicBudgetPlan, CostCenterBudgetLine
from ..schemas import StrategicBudgetPlanCreate

class BudgetPlanningService:
    @staticmethod
    async def create_annual_plan(
        session: AsyncSession,
        payload: StrategicBudgetPlanCreate,
        tenant_id: str,
        actor_id: str
    ) -> StrategicBudgetPlan:
        total_opex = Decimal("0.0")

        plan = StrategicBudgetPlan(
            tenant_id=tenant_id,
            fiscal_year=payload.fiscal_year,
            plan_name=payload.plan_name,
            version_type=payload.version_type,
            status="DRAFT_PREPARATION",
            total_revenue_budget=payload.total_revenue_budget,
            total_capex_budget=payload.total_capex_budget
        )
        session.add(plan)
        await session.flush()

        for cc in payload.cost_centers:
            annual_val = cc.monthly_uniform_amount * Decimal("12.0")
            total_opex += annual_val
            line = CostCenterBudgetLine(
                tenant_id=tenant_id,
                plan_id=plan.id,
                cost_center_code=cc.cost_center_code,
                cost_center_name=cc.cost_center_name,
                expense_type=cc.expense_type,
                month_01_amt=cc.monthly_uniform_amount,
                month_02_amt=cc.monthly_uniform_amount,
                month_03_amt=cc.monthly_uniform_amount,
                month_04_amt=cc.monthly_uniform_amount,
                month_05_amt=cc.monthly_uniform_amount,
                month_06_amt=cc.monthly_uniform_amount,
                month_07_amt=cc.monthly_uniform_amount,
                month_08_amt=cc.monthly_uniform_amount,
                month_09_amt=cc.monthly_uniform_amount,
                month_10_amt=cc.monthly_uniform_amount,
                month_11_amt=cc.monthly_uniform_amount,
                month_12_amt=cc.monthly_uniform_amount,
                total_annual_allocation=annual_val
            )
            session.add(line)

        plan.total_opex_budget = total_opex
        plan.net_ebitda_budget = payload.total_revenue_budget - total_opex
        if payload.total_revenue_budget > 0:
            plan.target_ebitda_margin_pct = ((plan.net_ebitda_budget / payload.total_revenue_budget) * Decimal("100.0")).quantize(Decimal("0.01"))

        await session.commit()
        await session.refresh(plan)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_BUDGET_PLAN",
            entity_type="StrategicBudgetPlan",
            entity_id=plan.id,
            description=f"Created FY{payload.fiscal_year} plan '{payload.plan_name}' EBITDA ${plan.net_ebitda_budget}"
        )
        return plan
