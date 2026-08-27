# NexERP

NexERP is a multi-tenant enterprise resource planning platform for finance,
procurement, inventory, manufacturing, sales, service, and workforce operations.

## Architecture

- **Backend:** FastAPI, SQLAlchemy 2 async, PostgreSQL in production, SQLite for local tests
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Operations:** Docker Compose, Redis, Celery, and Nginx
- **Security:** JWT authentication, tenant-scoped queries, RBAC permissions, hashed API keys

Every domain follows the same structure: models, schemas, services, routes, tests,
and audit-friendly state transitions. Business rules belong in services; routes
handle transport and permissions.

## Local Development

```powershell
# Backend
.\.venv\Scripts\python.exe -m pytest backend/tests -q

# Frontend
npm.cmd --prefix frontend install
npm.cmd --prefix frontend run build
```

The API is available at `/api/v1`, interactive documentation is at `/docs`,
and liveness/readiness probes are `/healthz` and `/readyz`.

## Production Startup

Set database, Redis, JWT, and allowed-origin values in the deployment environment.
Use a strong externally managed `JWT_SECRET_KEY`; never use the development
fallback in production. Start the complete stack with:

```powershell
docker compose up --build -d
```

The application runs migrations before Gunicorn starts. PostgreSQL and Redis
health checks gate application startup. Nginx serves the frontend and proxies API
traffic.

## Quality Gate

Run the standard-library syntax/configuration checks and backend regression suite:

```powershell
.\.venv\Scripts\python.exe backend/scripts/quality_gate.py
```

The test suite uses an isolated in-memory database and covers accounting,
inventory valuation, MRP, CRM, service operations, supply planning, security, and
manufacturing execution.
