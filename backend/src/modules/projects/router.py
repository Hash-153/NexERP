"""
NexERP Project Management & Professional Services (PSA) REST API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.projects.models import Project, Task, Timesheet
from backend.src.modules.projects.schemas import (
    ProjectCreate,
    ProjectResponse,
    TaskCreate,
    TaskResponse,
    TimesheetCreate,
    TimesheetResponse
)
from backend.src.modules.projects.services import ProjectService, TimesheetService

router = APIRouter(prefix="/projects", tags=["Project Management & Professional Services"])


# ==============================================================================
# Projects & WBS Tasks
# ==============================================================================

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: CurrentUser = Depends(RequirePermission("projects:projects:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List enterprise projects."""
    return await ProjectService.list_projects(db, current_user.tenant_id)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser = Depends(RequirePermission("projects:projects:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new project."""
    return await ProjectService.create_project(db, current_user.tenant_id, payload)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current_user: CurrentUser = Depends(RequirePermission("projects:projects:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Add a Work Breakdown Structure (WBS) task to a project."""
    return await ProjectService.create_task(db, current_user.tenant_id, payload)


# ==============================================================================
# Timesheets & Time Tracking
# ==============================================================================

@router.get("/timesheets", response_model=List[TimesheetResponse])
async def list_timesheets(
    employee_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("projects:timesheets:log")),
    db: AsyncSession = Depends(get_db_session)
):
    """List employee weekly timesheets."""
    return await TimesheetService.list_timesheets(db, current_user.tenant_id, employee_id)


@router.post("/timesheets", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
async def log_timesheet(
    payload: TimesheetCreate,
    current_user: CurrentUser = Depends(RequirePermission("projects:timesheets:log")),
    db: AsyncSession = Depends(get_db_session)
):
    """Submit a weekly timesheet."""
    return await TimesheetService.log_timesheet(db, current_user.tenant_id, payload)
