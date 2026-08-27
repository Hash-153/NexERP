"""Manufacturing execution calculation tests."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.manufacturing.execution_schemas import DowntimeCreate, OperatorSessionCreate, QualityCheckCreate, ScrapCreate, ScrapDecision
from backend.src.modules.manufacturing.execution_services import ManufacturingExecutionService


@pytest.mark.asyncio
async def test_operator_session_calculates_productive_hours_and_cost(db_session: AsyncSession):
    session = await ManufacturingExecutionService.create_session(db_session, "org_corp_hq_001", OperatorSessionCreate(job_card_id="job-001", operator_id="operator-001", started_at=datetime(2026, 7, 1, 8, tzinfo=timezone.utc), ended_at=datetime(2026, 7, 1, 17, tzinfo=timezone.utc), break_minutes=60, hourly_rate=Decimal("30")))
    assert session.productive_hours == Decimal("8.00")
    assert session.labor_cost == Decimal("240.00")
    assert session.status == "COMPLETED"


@pytest.mark.asyncio
async def test_quality_downtime_and_scrap_approval(db_session: AsyncSession):
    quality = await ManufacturingExecutionService.create_quality_check(db_session, "org_corp_hq_001", QualityCheckCreate(production_order_id="wo-001", checkpoint_code="DIM-01", checkpoint_name="Diameter", sample_size=Decimal("5"), accepted_quantity=Decimal("4"), rejected_quantity=Decimal("1"), measurement_value=Decimal("9.8"), lower_specification=Decimal("10"), upper_specification=Decimal("12")), "usr_admin_001")
    assert quality.result == "FAIL"
    downtime = await ManufacturingExecutionService.create_downtime(db_session, "org_corp_hq_001", DowntimeCreate(work_center_id="wc-001", started_at=datetime(2026, 7, 1, 10, tzinfo=timezone.utc), ended_at=datetime(2026, 7, 1, 11, 30, tzinfo=timezone.utc), category="BREAKDOWN", reason_code="MOTOR"), "usr_admin_001")
    assert downtime.duration_minutes == 90
    scrap = await ManufacturingExecutionService.request_scrap(db_session, "org_corp_hq_001", ScrapCreate(production_order_id="wo-001", quantity=Decimal("2"), unit_cost=Decimal("15"), reason_code="DIMENSION", explanation="Parts exceeded lower dimensional tolerance."), "usr_admin_001")
    assert scrap.total_cost == Decimal("30")
    decision = await ManufacturingExecutionService.decide_scrap(db_session, "org_corp_hq_001", scrap.id, ScrapDecision(status="APPROVED", disposition="REWORK"), "usr_admin_001")
    assert decision.status == "APPROVED"
