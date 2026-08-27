"""
NexERP Manufacturing Module.
"""

from .router import router as manufacturing_router
from . import execution_models

__all__ = ["manufacturing_router"]
