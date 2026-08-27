"""
NexERP Employee Expense Reimbursement Service.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.human_resources.models import ExpenseClaim, ExpenseClaimLine, Employee
from backend.src.modules.human_resources.schemas import ExpenseClaimCreate
from backend.src.modules.human_resources.enums import ExpenseClaimStatus


class ExpenseClaimService:
    """
    Employee travel & out-of-pocket reimbursement manager.
    """

    @classmethod
    async def generate_claim_number(cls, db: AsyncSession, tenant_id: str, claim_date: date) -> str:
        year_str = str(claim_date.year)
        prefix = f"EXP-{year_str}-"
        query = select(ExpenseClaim).where(ExpenseClaim.tenant_id == tenant_id).order_by(ExpenseClaim.claim_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.claim_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_expense_claim(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: ExpenseClaimCreate
    ) -> ExpenseClaim:
        emp_res = await db.execute(select(Employee).where(Employee.id == payload.employee_id, Employee.tenant_id == tenant_id))
        emp = emp_res.scalar_one_or_none()
        if not emp:
            raise EntityNotFoundError("Employee not found.")

        tot_amount = sum(l.amount for l in payload.lines)
        claim_num = await cls.generate_claim_number(db, tenant_id, payload.claim_date)

        claim = ExpenseClaim(
            tenant_id=tenant_id,
            claim_number=claim_num,
            employee_id=payload.employee_id,
            claim_date=payload.claim_date,
            total_amount=tot_amount,
            status=ExpenseClaimStatus.SUBMITTED.value
        )
        db.add(claim)
        await db.flush()

        for line in payload.lines:
            c_line = ExpenseClaimLine(
                tenant_id=tenant_id,
                expense_claim_id=claim.id,
                expense_date=line.expense_date,
                category=line.category,
                description=line.description.strip(),
                amount=line.amount,
                expense_account_id=line.expense_account_id
            )
            db.add(c_line)

        await db.commit()
        await db.refresh(claim)
        return claim

    @classmethod
    async def list_expense_claims(cls, db: AsyncSession, tenant_id: str, employee_id: Optional[str] = None) -> List[ExpenseClaim]:
        query = (
            select(ExpenseClaim)
            .where(ExpenseClaim.tenant_id == tenant_id, ExpenseClaim.is_deleted == False)
            .options(selectinload(ExpenseClaim.lines))
            .order_by(ExpenseClaim.claim_date.desc())
        )
        if employee_id:
            query = query.where(ExpenseClaim.employee_id == employee_id)
        res = await db.execute(query)
        return list(res.scalars().all())
