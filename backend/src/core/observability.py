"""Production request observability primitives with no external monitoring dependency."""

import time
import uuid
from collections import Counter
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .logging_config import get_logger

logger = get_logger("nexerp.http")
request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


@dataclass
class RequestMetric:
    """Aggregated counters suitable for a scrape endpoint or log exporter."""

    requests: int = 0
    errors: int = 0
    total_duration_ms: float = 0.0


_metrics: Dict[str, RequestMetric] = {}
_status_counts: Counter[str] = Counter()


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Adds correlation IDs, security headers, timing, and request counters."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_context.set(request_id)
        started = time.perf_counter()
        route = request.url.path
        metric = _metrics.setdefault(route, RequestMetric())
        metric.requests += 1
        try:
            response = await call_next(request)
        except Exception:
            metric.errors += 1
            _status_counts["500"] += 1
            logger.exception("Unhandled request error", extra={"request_id": request_id, "path": route})
            raise
        finally:
            elapsed = (time.perf_counter() - started) * 1000
            metric.total_duration_ms += elapsed
            request_id_context.reset(token)
        _status_counts[str(response.status_code)] += 1
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


def metrics_snapshot() -> dict:
    """Return a JSON-safe snapshot for diagnostics and container monitoring."""
    routes = {}
    for route, metric in _metrics.items():
        routes[route] = {
            "requests": metric.requests,
            "errors": metric.errors,
            "average_duration_ms": round(metric.total_duration_ms / metric.requests, 2) if metric.requests else 0,
        }
    return {"status_counts": dict(_status_counts), "routes": routes}


def reset_metrics() -> None:
    """Reset in-memory counters in tests or after a metrics scrape interval."""
    _metrics.clear()
    _status_counts.clear()
