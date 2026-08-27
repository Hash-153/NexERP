"""
NexERP Project Scheduling & Work Breakdown Structure Service.
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.projects.models import Project, Milestone, Task
from backend.src.modules.projects.schemas import ProjectCreate, MilestoneCreate, TaskCreate
from backend.src.modules.projects.enums import ProjectStatus, TaskStatus


class ProjectService:
    """
    Project lifecycle and task manager.
    """

    @classmethod
    async def generate_project_number(cls, db: AsyncSession, tenant_id: str, start_date: date) -> str:
        year_str = str(start_date.year)
        prefix = f"PRJ-{year_str}-"
        query = select(Project).where(Project.tenant_id == tenant_id).order_by(Project.project_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.project_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_project(cls, db: AsyncSession, tenant_id: str, payload: ProjectCreate) -> Project:
        prj_num = await cls.generate_project_number(db, tenant_id, payload.start_date)
        project = Project(
            tenant_id=tenant_id,
            project_number=prj_num,
            name=payload.name.strip(),
            customer_id=payload.customer_id,
            manager_id=payload.manager_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            budget_amount=payload.budget_amount,
            billing_type=payload.billing_type.value,
            currency=payload.currency.upper(),
            status=ProjectStatus.ACTIVE.value,
            notes=payload.notes
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @classmethod
    async def create_task(cls, db: AsyncSession, tenant_id: str, payload: TaskCreate) -> Task:
        task_num = f"TSK-{date.today().strftime('%y%m%d%H%M%S')}"
        task = Task(
            tenant_id=tenant_id,
            project_id=payload.project_id,
            milestone_id=payload.milestone_id,
            task_number=task_num,
            title=payload.title.strip(),
            description=payload.description,
            assigned_to_id=payload.assigned_to_id,
            estimated_hours=payload.estimated_hours,
            priority=payload.priority.value,
            status=TaskStatus.TODO.value,
            start_date=payload.start_date,
            due_date=payload.due_date
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @classmethod
    async def list_projects(cls, db: AsyncSession, tenant_id: str) -> List[Project]:
        query = (
            select(Project)
            .where(Project.tenant_id == tenant_id, Project.is_deleted == False)
            .options(selectinload(Project.tasks), selectinload(Project.milestones))
            .order_by(Project.created_at.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
