"""Security administration credential and feature flag tests."""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.auth.admin_services import SecurityAdministrationService


@pytest.mark.asyncio
async def test_api_key_is_hashed_and_revocable(db_session: AsyncSession):
    raw, key = await SecurityAdministrationService.issue_api_key(db_session, "org_corp_hq_001", "Integration client", ["sales:read", "inventory:read"], "usr_admin_001", datetime.now(timezone.utc) + timedelta(days=1))
    assert raw not in key.key_hash
    validated = await SecurityAdministrationService.authenticate_api_key(db_session, "org_corp_hq_001", raw)
    assert validated.id == key.id
    await SecurityAdministrationService.revoke_api_key(db_session, "org_corp_hq_001", key.id)
    with pytest.raises(ValueError, match="invalid"):
        await SecurityAdministrationService.authenticate_api_key(db_session, "org_corp_hq_001", raw)


@pytest.mark.asyncio
async def test_feature_flags_are_tenant_scoped(db_session: AsyncSession):
    await SecurityAdministrationService.set_feature_flag(db_session, "org_corp_hq_001", "advanced_forecast", True, "usr_admin_001")
    assert await SecurityAdministrationService.enabled(db_session, "org_corp_hq_001", "advanced_forecast") is True
    assert await SecurityAdministrationService.enabled(db_session, "org_other", "advanced_forecast") is False
    with pytest.raises(ValueError, match="Unsupported"):
        await SecurityAdministrationService.record_login(db_session, "org_corp_hq_001", "UNKNOWN")
