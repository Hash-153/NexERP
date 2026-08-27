"""
NexERP Employee Master & Organization Hierarchy Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.human_resources.models import Department, JobPosition, Employee
from backend.src.modules.human_resources.schemas import DepartmentCreate, JobPositionCreate, EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """
    Employee directory and departmental hierarchy service.
    """

    @classmethod
    async def create_department(cls, db: AsyncSession, tenant_id: str, payload: DepartmentCreate) -> Department:
        query = select(Department).where(Department.tenant_id == tenant_id, Department.code == payload.code.upper().strip())
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Department '{payload.code}' already exists.")

        dept = Department(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            manager_id=payload.manager_id,
            cost_center_id=payload.cost_center_id
        )
        db.add(dept)
        await db.commit()
        await db.refresh(dept)
        return dept

    @classmethod
    async def list_departments(cls, db: AsyncSession, tenant_id: str) -> List[Department]:
        query = select(Department).where(Department.tenant_id == tenant_id, Department.is_deleted == False).order_by(Department.code.asc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def create_job_position(cls, db: AsyncSession, tenant_id: str, payload: JobPositionCreate) -> JobPosition:
        job = JobPosition(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            title=payload.title.strip(),
            department_id=payload.department_id,
            grade_level=payload.grade_level
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @classmethod
    async def list_job_positions(cls, db: AsyncSession, tenant_id: str) -> List[JobPosition]:
        query = select(JobPosition).where(JobPosition.tenant_id == tenant_id, JobPosition.is_deleted == False).order_by(JobPosition.title.asc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def create_employee(cls, db: AsyncSession, tenant_id: str, payload: EmployeeCreate) -> Employee:
        query = select(Employee).where(
            Employee.tenant_id == tenant_id,
            Employee.employee_number == payload.employee_number.upper().strip(),
            Employee.is_deleted == False
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Employee number '{payload.employee_number}' already exists.")

        emp = Employee(
            tenant_id=tenant_id,
            employee_number=payload.employee_number.upper().strip(),
            user_id=payload.user_id,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=payload.email.lower().strip(),
            phone=payload.phone,
            date_of_birth=payload.date_of_birth,
            date_of_joining=payload.date_of_joining,
            department_id=payload.department_id,
            job_position_id=payload.job_position_id,
            reports_to_id=payload.reports_to_id,
            employment_status=payload.employment_status.value,
            national_tax_id=payload.national_tax_id,
            bank_account_number=payload.bank_account_number,
            bank_name=payload.bank_name,
            base_salary=payload.base_salary,
            currency=payload.currency.upper()
        )
        db.add(emp)
        await db.commit()
        await db.refresh(emp)
        return emp

    @classmethod
    async def list_employees(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        query = (
            select(Employee)
            .where(Employee.tenant_id == tenant_id, Employee.is_deleted == False)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_position)
            )
            .order_by(Employee.employee_number.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(query)
        return list(res.scalars().all())
