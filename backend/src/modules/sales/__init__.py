"""
NexERP Sales Module.
"""

from .router import router as sales_router
from . import crm_models

__all__ = ["sales_router"]
