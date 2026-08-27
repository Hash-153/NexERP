# Operations Runbook

## Health Checks

- `/healthz` confirms the process is alive.
- `/readyz` executes `SELECT 1` against the configured database.
- `/metrics` exposes low-cardinality in-memory request counters and average latency.
- Every response includes `X-Request-ID`; provide that value when investigating a request.

## Deployment Checklist

1. Provide a unique production JWT secret through the secret manager.
2. Set explicit `DATABASE_URL`, `REDIS_URL`, and `ALLOWED_ORIGINS` values.
3. Build the frontend and publish its `dist` directory to the Nginx container.
4. Run `docker compose config` and review rendered environment values.
5. Start PostgreSQL and Redis, wait for healthy status, then start the application.
6. Verify `/healthz`, `/readyz`, `/docs`, login, and one authenticated API route.
7. Confirm backups and restore drills are current.

## Incident Response

Capture the request ID, tenant ID, endpoint, response status, and timestamp. Check
application JSON logs first, then database and Redis health. Avoid placing access
tokens, passwords, or raw API keys in tickets or log messages. API keys are only
shown once at creation and can be revoked from the security administration flow.

## Financial Close

Create the required checklist items for a fiscal period, attach evidence when each
is completed, inspect the readiness endpoint, and lock only after all required
controls are complete. Reconciliation exceptions must be resolved or explicitly
carried with an approved control note before close.
