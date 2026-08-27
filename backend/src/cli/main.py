"""
NexERP Interactive Command Line Administration Suite (CLI).
Enables DevOps and System Administrators to run database migrations, seed data,
trigger MRP calculations, run payroll batches, and inspect general ledger status from the terminal.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from datetime import date
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="NexERP Enterprise Administration & Automation CLI")
console = Console()


@app.command()
def seed():
    """Seed database with full Apex Dynamics Industrial Corp enterprise demo dataset."""
    from backend.scripts.seed_demo_data import seed_enterprise_data
    console.print(Panel.fit("[bold green]Starting NexERP Enterprise Data Seeder...[/bold green]"))
    asyncio.run(seed_enterprise_data())


@app.command()
def run_mrp(horizon_days: int = 90, tenant_id: str = "org_corp_hq_001"):
    """Execute MRP planning explosion calculation across all demand and BOM recipes."""
    from backend.src.core.database import AsyncSessionLocal
    from backend.src.modules.manufacturing.services import MRPEngineService

    async def _run():
        async with AsyncSessionLocal() as session:
            snapshot = await MRPEngineService.run_mrp_calculation(
                session, tenant_id, planning_horizon_days=horizon_days, user_id="CLI"
            )
            console.print(Panel.fit(
                f"[bold cyan]MRP Calculation Completed Successfully![/bold cyan]\n"
                f"Snapshot ID: {snapshot.id}\n"
                f"Planned Orders Generated: [bold yellow]{snapshot.total_planned_orders}[/bold yellow]\n"
                f"Planning Horizon: {horizon_days} days"
            ))

    asyncio.run(_run())


@app.command()
def show_kpis(tenant_id: str = "org_corp_hq_001"):
    """Display real-time executive dashboard KPIs in terminal."""
    from backend.src.core.database import AsyncSessionLocal
    from backend.src.modules.analytics.services import ExecutiveDashboardService

    async def _run():
        async with AsyncSessionLocal() as session:
            data = await ExecutiveDashboardService.get_dashboard_summary(session, tenant_id, date.today())
            
            table = Table(title=f"NexERP Executive Dashboard - {data.as_of_date}", style="cyan")
            table.add_column("Metric Description", style="bold white")
            table.add_column("Current Value", style="bold green")

            table.add_row("YTD Net Sales Revenue", f"${data.kpis.total_revenue_ytd:,.2f}")
            table.add_row("Gross Margin %", f"{data.kpis.gross_margin_percentage:.2f}%")
            table.add_row("Cash & Bank Reserves", f"${data.kpis.cash_and_bank_balance:,.2f}")
            table.add_row("Accounts Receivable (AR)", f"${data.kpis.accounts_receivable_outstanding:,.2f}")
            table.add_row("Accounts Payable (AP)", f"${data.kpis.accounts_payable_outstanding:,.2f}")
            table.add_row("Total Warehouse Inventory Value", f"${data.kpis.total_inventory_valuation:,.2f}")
            table.add_row("Open Sales Orders Backlog", f"${data.kpis.open_sales_orders_value:,.2f}")
            table.add_row("Active Production Orders", str(data.kpis.open_production_orders_count))
            table.add_row("Active Employees", str(data.kpis.active_employees_count))

            console.print(table)

    asyncio.run(_run())


if __name__ == "__main__":
    app()
