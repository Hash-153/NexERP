"""NexERP notifications and workflow automation module."""

from . import models
from .router import router as workflow_automation_router

__all__ = ["workflow_automation_router"]
