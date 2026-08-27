"""
Fixed Assets Services Package.
"""
from .depreciation_engine_service import DepreciationEngineService
from .asset_lifecycle_service import AssetLifecycleService

__all__ = ["DepreciationEngineService", "AssetLifecycleService"]
