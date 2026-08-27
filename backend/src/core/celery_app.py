"""
NexERP Enterprise - Celery Async Task Queue Configuration.
Provides background task processing for:
- Scheduled payroll runs
- MRP netting & explosion
- Long-running report generation
- Email notification dispatch
- Currency revaluation batch jobs.
"""

from celery import Celery
from celery.schedules import crontab

from backend.src.core.config import get_settings


def create_celery_app() -> Celery:
    """
    Factory function: creates and configures the Celery application instance.
    """
    settings = get_settings()

    broker_url = settings.celery_broker_url or settings.redis_url or "redis://localhost:6379/1"
    result_backend = settings.celery_result_backend or settings.redis_url or "redis://localhost:6379/2"

    app = Celery(
        "nexerp",
        broker=broker_url,
        backend=result_backend,
        include=[
            "backend.src.tasks.payroll_tasks",
            "backend.src.tasks.mrp_tasks",
            "backend.src.tasks.report_tasks",
            "backend.src.tasks.notification_tasks",
        ]
    )

    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=1,
        task_routes={
            "backend.src.tasks.payroll_tasks.*": {"queue": "payroll"},
            "backend.src.tasks.mrp_tasks.*": {"queue": "mrp"},
            "backend.src.tasks.report_tasks.*": {"queue": "reports"},
            "backend.src.tasks.notification_tasks.*": {"queue": "default"},
        },
        beat_schedule={
            # Run MRP netting every weekday at 06:00 UTC
            "daily-mrp-run": {
                "task": "backend.src.tasks.mrp_tasks.run_nightly_mrp",
                "schedule": crontab(hour=6, minute=0, day_of_week="mon-fri"),
            },
            # Run monthly payroll on 25th of each month at 07:00 UTC
            "monthly-payroll-calculation": {
                "task": "backend.src.tasks.payroll_tasks.calculate_monthly_payroll",
                "schedule": crontab(hour=7, minute=0, day_of_month=25),
            },
            # Send daily DSO/AR aging summary to CFO at 08:00 UTC
            "daily-ar-aging-report": {
                "task": "backend.src.tasks.report_tasks.send_ar_aging_report",
                "schedule": crontab(hour=8, minute=0),
            },
            # Run FX revaluation at month-end on the last calendar day at 20:00 UTC
            "month-end-fx-revaluation": {
                "task": "backend.src.tasks.payroll_tasks.run_fx_revaluation",
                "schedule": crontab(hour=20, minute=0, day_of_month="28,29,30,31"),
            }
        }
    )

    return app


celery_app = create_celery_app()
