"""Production health and request observability checks."""

import pytest
from httpx import AsyncClient
from backend.src.core.observability import reset_metrics


@pytest.mark.asyncio
async def test_health_has_security_headers_and_request_id(client: AsyncClient):
    reset_metrics()
    response = await client.get("/healthz", headers={"X-Request-ID": "test-request-001"})
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.headers["X-Request-ID"] == "test-request-001"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


@pytest.mark.asyncio
async def test_container_health_alias_and_metrics(client: AsyncClient):
    reset_metrics()
    health = await client.get("/api/v1/health")
    metrics = await client.get("/metrics")
    assert health.status_code == 200
    assert metrics.status_code == 200
    assert metrics.json()["status_counts"]["200"] >= 1
    assert "/api/v1/health" in metrics.json()["routes"]
