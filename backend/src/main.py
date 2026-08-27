"""
NexERP Core Application Entrypoint & API Gateway.
Wires middleware, database lifecycle, exception interceptors, and business domain routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.src.core.config import settings
from backend.src.core.database import init_db_engine, AsyncSessionLocal
from backend.src.core.exceptions import NexERPBaseException
from backend.src.modules.auth.services import RBACService
from backend.src.modules.auth import auth_router
from backend.src.modules.financials import financials_router
from backend.src.modules.accounts_payable import accounts_payable_router
from backend.src.modules.accounts_receivable import accounts_receivable_router
from backend.src.modules.inventory import inventory_router
from backend.src.modules.procurement import procurement_router
from backend.src.modules.sales import sales_router
from backend.src.modules.manufacturing import manufacturing_router
from backend.src.modules.quality_control import quality_control_router
from backend.src.modules.human_resources import human_resources_router
from backend.src.modules.projects import projects_router
from backend.src.modules.analytics import analytics_router
from backend.src.modules.governance import router as governance_router
from backend.src.modules.service_management import service_management_router
from backend.src.modules.supply_planning import supply_planning_router
from backend.src.modules.financial_controls import financial_controls_router
from backend.src.modules.workflow_automation import workflow_automation_router
from backend.src.modules.treasury_cash_management import treasury_router
from backend.src.modules.fixed_assets_management import fixed_assets_router
from backend.src.modules.warehouse_advanced_wms import advanced_wms_router
from backend.src.modules.logistics_fleet_management import logistics_fleet_router
from backend.src.modules.crm_leads_opportunities import crm_router
from backend.src.modules.field_service_operations import field_service_router
from backend.src.modules.contract_lifecycle_management import contract_management_router
from backend.src.modules.compliance_esg_reporting import esg_compliance_router
from backend.src.modules.budgeting_strategic_planning import strategic_budgeting_router
from backend.src.modules.production_scheduling_aps import production_scheduling_router
from backend.src.modules.vendor_portal_collaboration import vendor_portal_router
from backend.src.modules.customer_portal_self_service import customer_portal_router
from backend.src.modules.tax_engine import tax_engine_router
from backend.src.modules.audit_compliance import audit_compliance_router
from backend.src.modules.quality_assurance_iso import quality_assurance_iso_router
from backend.src.modules.e_invoicing_peppol import e_invoicing_peppol_router
from backend.src.modules.subscription_recurring_billing import subscription_billing_router
from backend.src.modules.predictive_maintenance_iot import predictive_maintenance_iot_router
from backend.src.core.observability import RequestObservabilityMiddleware, metrics_snapshot


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle hook.
    Initializes database tables and seeds system authorization permissions.
    """
    # 1. Initialize schema
    await init_db_engine()

    # 2. Seed system RBAC permissions
    async with AsyncSessionLocal() as session:
        await RBACService.seed_permissions(session)

    yield

    # Teardown / cleanup resources if necessary


app = FastAPI(
    title=settings.APP_NAME,
    description="NexERP - Modular Enterprise Resource Planning Platform adhering to GAAP/IFRS standards, MRP-II mechanics, and multi-tenant security.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestObservabilityMiddleware)


# Global Exception Interceptor for Domain Exceptions
@app.exception_handler(NexERPBaseException)
async def nexerp_exception_handler(request: Request, exc: NexERPBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


# Register Core Domain Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(financials_router, prefix=settings.API_V1_PREFIX)
app.include_router(accounts_payable_router, prefix=settings.API_V1_PREFIX)
app.include_router(accounts_receivable_router, prefix=settings.API_V1_PREFIX)
app.include_router(inventory_router, prefix=settings.API_V1_PREFIX)
app.include_router(procurement_router, prefix=settings.API_V1_PREFIX)
app.include_router(sales_router, prefix=settings.API_V1_PREFIX)
app.include_router(manufacturing_router, prefix=settings.API_V1_PREFIX)
app.include_router(quality_control_router, prefix=settings.API_V1_PREFIX)
app.include_router(human_resources_router, prefix=settings.API_V1_PREFIX)
app.include_router(projects_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
app.include_router(governance_router, prefix=settings.API_V1_PREFIX)
app.include_router(service_management_router, prefix=settings.API_V1_PREFIX)
app.include_router(supply_planning_router, prefix=settings.API_V1_PREFIX)
app.include_router(financial_controls_router, prefix=settings.API_V1_PREFIX)
app.include_router(workflow_automation_router, prefix=settings.API_V1_PREFIX)
app.include_router(treasury_router, prefix=settings.API_V1_PREFIX)
app.include_router(fixed_assets_router, prefix=settings.API_V1_PREFIX)
app.include_router(advanced_wms_router, prefix=settings.API_V1_PREFIX)
app.include_router(logistics_fleet_router, prefix=settings.API_V1_PREFIX)
app.include_router(crm_router, prefix=settings.API_V1_PREFIX)
app.include_router(field_service_router, prefix=settings.API_V1_PREFIX)
app.include_router(contract_management_router, prefix=settings.API_V1_PREFIX)
app.include_router(esg_compliance_router, prefix=settings.API_V1_PREFIX)
app.include_router(strategic_budgeting_router, prefix=settings.API_V1_PREFIX)
app.include_router(production_scheduling_router, prefix=settings.API_V1_PREFIX)
app.include_router(vendor_portal_router, prefix=settings.API_V1_PREFIX)
app.include_router(customer_portal_router, prefix=settings.API_V1_PREFIX)
app.include_router(tax_engine_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_compliance_router, prefix=settings.API_V1_PREFIX)
app.include_router(quality_assurance_iso_router, prefix=settings.API_V1_PREFIX)
app.include_router(e_invoicing_peppol_router, prefix=settings.API_V1_PREFIX)
app.include_router(subscription_billing_router, prefix=settings.API_V1_PREFIX)
app.include_router(predictive_maintenance_iot_router, prefix=settings.API_V1_PREFIX)


@app.get("/healthz", tags=["System Health"])
async def health_check():
    """Liveness probe returning healthy system status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/health", tags=["System Health"])
async def container_health_check():
    """Compatibility health route used by Docker and reverse-proxy probes."""
    return await health_check()


@app.get("/readyz", tags=["System Health"])
async def readiness_check():
    """Readiness probe that verifies the configured database is reachable."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@app.get("/metrics", tags=["System Health"])
async def metrics():
    """Expose low-cardinality request metrics for container diagnostics."""
    return metrics_snapshot()
