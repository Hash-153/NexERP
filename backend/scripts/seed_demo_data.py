"""
NexERP Comprehensive Enterprise Demo Database Seeder.
Populates realistic industrial manufacturing dataset: "Apex Dynamics Industrial Corp"
spanning Chart of Accounts, multi-tier BOMs, warehouses, suppliers, customers, employees, and transactions.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.future import select

from backend.src.core.database import AsyncSessionLocal, init_db_engine, async_engine, Base
from backend.src.core.security import hash_password
from backend.src.modules.auth.models import Tenant, User, Role, Permission, UserRole, RolePermission
from backend.src.modules.auth.services import RBACService
from backend.src.modules.financials.models import Account, FiscalYear, FiscalPeriod, TaxCategory, TaxRate
from backend.src.modules.financials.services import GeneralLedgerService, FiscalPeriodService
from backend.src.modules.financials.schemas import FiscalYearCreate, JournalEntryCreate, JournalEntryLineCreate
from backend.src.modules.inventory.models import UnitOfMeasure, ItemCategory, Item, Warehouse, WarehouseLocation
from backend.src.modules.inventory.services import CostingValuationService, StockMovementService
from backend.src.modules.inventory.schemas import StockMovementCreate, StockMovementLineCreate
from backend.src.modules.inventory.enums import MovementType
from backend.src.modules.accounts_payable.models import Vendor
from backend.src.modules.accounts_payable.services import VendorService, VendorBillService
from backend.src.modules.accounts_payable.schemas import VendorCreate, VendorBillCreate, VendorBillLineCreate
from backend.src.modules.accounts_receivable.models import Customer
from backend.src.modules.accounts_receivable.services import CustomerService, SalesInvoiceService
from backend.src.modules.accounts_receivable.schemas import CustomerCreate, SalesInvoiceCreate, SalesInvoiceLineCreate
from backend.src.modules.manufacturing.models import WorkCenter, BillOfMaterials, BOMLine, Routing, RoutingOperation
from backend.src.modules.manufacturing.services import BOMService, ProductionOrderService
from backend.src.modules.manufacturing.schemas import BOMCreate, BOMLineCreate, ProductionOrderCreate
from backend.src.modules.human_resources.models import Department, JobPosition, Employee
from backend.src.modules.human_resources.services import EmployeeService, PayrollCalculationService
from backend.src.modules.human_resources.schemas import DepartmentCreate, JobPositionCreate, EmployeeCreate, PayrollRunCreate
from backend.src.modules.projects.services import ProjectService
from backend.src.modules.projects.schemas import ProjectCreate, TaskCreate


async def seed_enterprise_data():
    print("==========================================================")
    print("[*] Initializing NexERP Enterprise Database Seed Process...")
    print("==========================================================")

    # Clean reset & initialize schema
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Permissions
        print("-> Seeding RBAC Permissions...")
        await RBACService.seed_permissions(session)

        # 2. Provision Tenant
        print("-> Provisioning Tenant: Apex Dynamics Industrial Corp...")
        tenant_id = "org_corp_hq_001"
        tenant = Tenant(
            id=tenant_id,
            name="Apex Dynamics Industrial Corp",
            code="APEX-IND",
            currency="USD",
            tax_identifier="EIN-88-2918291",
            country="United States",
            timezone="America/New_York",
            fiscal_year_start_month="January",
            is_active=True
        )
        session.add(tenant)
        await session.flush()

        # 3. Create Admin & Management Users
        print("-> Creating System Users & Assigning Roles...")
        admin_role = Role(tenant_id=tenant_id, name="SuperAdmin", description="Full unrestricted administrative access", is_system_role=True)
        finance_role = Role(tenant_id=tenant_id, name="CFO", description="Chief Financial Officer & Finance Management", is_system_role=True)
        ops_role = Role(tenant_id=tenant_id, name="OperationsDirector", description="Plant operations and supply chain management", is_system_role=True)
        session.add_all([admin_role, finance_role, ops_role])
        await session.flush()

        admin_user = User(
            tenant_id=tenant_id,
            email="admin@apexdynamics.com",
            hashed_password=hash_password("AdminPass123!"),
            first_name="Alexander",
            last_name="Vance",
            phone_number="+1-555-019-2831",
            is_superuser=True,
            is_active=True
        )
        cfo_user = User(
            tenant_id=tenant_id,
            email="cfo@apexdynamics.com",
            hashed_password=hash_password("FinancePass123!"),
            first_name="Eleanor",
            last_name="Sterling",
            phone_number="+1-555-019-4492",
            is_superuser=False,
            is_active=True
        )
        ops_user = User(
            tenant_id=tenant_id,
            email="operations@apexdynamics.com",
            hashed_password=hash_password("OpsPass123!"),
            first_name="Marcus",
            last_name="Kane",
            phone_number="+1-555-019-7711",
            is_superuser=False,
            is_active=True
        )
        session.add_all([admin_user, cfo_user, ops_user])
        await session.flush()

        session.add(UserRole(tenant_id=tenant_id, user_id=admin_user.id, role_id=admin_role.id))
        session.add(UserRole(tenant_id=tenant_id, user_id=cfo_user.id, role_id=finance_role.id))
        session.add(UserRole(tenant_id=tenant_id, user_id=ops_user.id, role_id=ops_role.id))
        await session.commit()

    async with AsyncSessionLocal() as session:
        # 4. Chart of Accounts (COA)
        print("-> Setting up GAAP Chart of Accounts...")
        coa_data = [
            ("10100", "Operating Bank Account - Chase", "ASSET", "CASH_AND_BANK", True),
            ("10200", "Payroll Disbursement Account", "ASSET", "CASH_AND_BANK", True),
            ("11000", "Accounts Receivable Control", "ASSET", "ACCOUNTS_RECEIVABLE", True),
            ("12000", "Raw Materials Inventory", "ASSET", "INVENTORY", True),
            ("12100", "Work in Progress (WIP)", "ASSET", "INVENTORY", True),
            ("12200", "Finished Goods Inventory", "ASSET", "INVENTORY", True),
            ("15000", "Plant Machinery & Equipment", "ASSET", "PROPERTY_PLANT_EQUIPMENT", False),
            ("15900", "Accumulated Depreciation - Machinery", "ASSET", "ACCUMULATED_DEPRECIATION", False),
            ("20100", "Accounts Payable Control", "LIABILITY", "ACCOUNTS_PAYABLE", True),
            ("21000", "Sales Tax Output Payable", "LIABILITY", "TAX_PAYABLE", False),
            ("22000", "Salaries & Wages Payable", "LIABILITY", "PAYROLL_PAYABLE", False),
            ("22100", "Payroll Tax Withholding Liability", "LIABILITY", "TAX_PAYABLE", False),
            ("30100", "Common Stock / Paid-in Capital", "EQUITY", "SHARE_CAPITAL", False),
            ("30200", "Retained Earnings", "EQUITY", "RETAINED_EARNINGS", False),
            ("40100", "Finished Machinery Sales Revenue", "REVENUE", "OPERATING_REVENUE", False),
            ("40200", "Engineering Services Revenue", "REVENUE", "OPERATING_REVENUE", False),
            ("50100", "Cost of Goods Sold - Manufacturing", "EXPENSE", "COST_OF_GOODS_SOLD", False),
            ("60100", "Salaries & Wages Expense", "EXPENSE", "SALARIES_AND_WAGES", False),
            ("60200", "Plant Depreciation Expense", "EXPENSE", "DEPRECIATION_EXPENSE", False),
            ("60300", "Facility Power & Utilities", "EXPENSE", "GENERAL_AND_ADMIN", False),
            ("60400", "Freight & Logistics Expense", "EXPENSE", "GENERAL_AND_ADMIN", False),
        ]
        accounts_map = {}
        for code, name, a_type, classification, rec in coa_data:
            acc = Account(
                tenant_id=tenant_id,
                code=code,
                name=name,
                account_type=a_type,
                classification=classification,
                currency="USD",
                is_reconcilable=rec,
                current_balance=Decimal("0.0")
            )
            session.add(acc)
            accounts_map[code] = acc
        await session.flush()

        # 5. Fiscal Calendar
        print("-> Setting up FY 2026 Fiscal Year & 12 Periods...")
        fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
            session,
            tenant_id,
            FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
        )
        current_period = fy.periods[0]

        # 6. Tax Rates
        tax_cat = TaxCategory(tenant_id=tenant_id, name="Standard Commercial Tax", code="STD_TAX")
        session.add(tax_cat)
        await session.flush()
        tax_rate = TaxRate(
            tenant_id=tenant_id,
            category_id=tax_cat.id,
            code="NY_SALES_TAX",
            name="New York State & Local Sales Tax",
            rate_percent=Decimal("8.8750"),
            sales_account_id=accounts_map["21000"].id,
            is_recoverable=True
        )
        session.add(tax_rate)
        await session.commit()

    async with AsyncSessionLocal() as session:
        # 7. Initial Capital Investment Journal Voucher ($1,000,000)
        print("-> Posting Opening Capital Investment ($1,000,000)...")
        # Re-fetch accounts
        bank_acc = (await session.execute(select(Account).where(Account.tenant_id == tenant_id, Account.code == "10100"))).scalar_one()
        capital_acc = (await session.execute(select(Account).where(Account.tenant_id == tenant_id, Account.code == "30100"))).scalar_one()
        p_res = await session.execute(select(FiscalPeriod).where(FiscalPeriod.tenant_id == tenant_id).limit(1))
        period = p_res.scalar_one()

        jv_payload = JournalEntryCreate(
            entry_date=date(2026, 1, 1),
            period_id=period.id,
            reference="OPENING-CAPITAL",
            narration="Initial Equity Capital Injection for Apex Dynamics Industrial Corp",
            lines=[
                JournalEntryLineCreate(account_id=bank_acc.id, debit=Decimal("1000000.00"), credit=Decimal("0.0"), description="Chase Operating Account Initial Funding"),
                JournalEntryLineCreate(account_id=capital_acc.id, debit=Decimal("0.0"), credit=Decimal("1000000.00"), description="Common Shares Authorized and Paid-In"),
            ]
        )
        jv = await GeneralLedgerService.create_journal_entry(session, tenant_id, jv_payload)
        await GeneralLedgerService.post_journal_entry(session, tenant_id, jv.id, "system")

        # 8. Units of Measure
        print("-> Setting up Units of Measure...")
        uom_ea = UnitOfMeasure(tenant_id=tenant_id, code="EA", name="Each / Units", category="Quantity")
        uom_kg = UnitOfMeasure(tenant_id=tenant_id, code="KG", name="Kilograms", category="Weight")
        uom_mtr = UnitOfMeasure(tenant_id=tenant_id, code="MTR", name="Meters", category="Length")
        session.add_all([uom_ea, uom_kg, uom_mtr])
        await session.flush()

        # 9. Item Categories
        raw_cat = ItemCategory(tenant_id=tenant_id, code="RAW", name="Raw Materials & Castings", valuation_method="FIFO")
        sub_cat = ItemCategory(tenant_id=tenant_id, code="SUB", name="Manufactured Subassemblies", valuation_method="FIFO")
        fg_cat = ItemCategory(tenant_id=tenant_id, code="FG", name="Finished Industrial Machinery", valuation_method="FIFO")
        session.add_all([raw_cat, sub_cat, fg_cat])
        await session.flush()

        # 10. Items Master Catalog
        print("-> Seeding Items Catalog (Finished Pumps, Subassemblies & Raw Materials)...")
        item_fg = Item(
            tenant_id=tenant_id,
            sku="HYD-PUMP-500",
            name="5000 PSI Hydraulic Triplex Pump Assembly",
            category_id=fg_cat.id,
            uom_id=uom_ea.id,
            item_type="FINISHED_GOOD",
            standard_cost=Decimal("1450.00"),
            moving_average_cost=Decimal("1450.00"),
            list_price=Decimal("3200.00"),
            lead_time_days=14,
            safety_stock=Decimal("10.0")
        )
        item_sub = Item(
            tenant_id=tenant_id,
            sku="SUB-VALVE-BLOCK",
            name="High-Pressure Hydraulic Manifold Block Subassembly",
            category_id=sub_cat.id,
            uom_id=uom_ea.id,
            item_type="WORK_IN_PROGRESS",
            standard_cost=Decimal("420.00"),
            moving_average_cost=Decimal("420.00"),
            list_price=Decimal("850.00"),
            lead_time_days=7,
            safety_stock=Decimal("20.0")
        )
        item_steel = Item(
            tenant_id=tenant_id,
            sku="RM-STEEL-BILLET",
            name="Forged Alloy Steel Round Billet 100mm x 500mm",
            category_id=raw_cat.id,
            uom_id=uom_ea.id,
            item_type="RAW_MATERIAL",
            standard_cost=Decimal("110.00"),
            moving_average_cost=Decimal("110.00"),
            list_price=Decimal("0.00"),
            lead_time_days=10,
            safety_stock=Decimal("50.0")
        )
        item_motor = Item(
            tenant_id=tenant_id,
            sku="RM-MOTOR-15HP",
            name="15 HP Three-Phase Severe-Duty Induction Motor 460V",
            category_id=raw_cat.id,
            uom_id=uom_ea.id,
            item_type="RAW_MATERIAL",
            standard_cost=Decimal("650.00"),
            moving_average_cost=Decimal("650.00"),
            list_price=Decimal("0.00"),
            lead_time_days=14,
            safety_stock=Decimal("15.0")
        )
        item_seals = Item(
            tenant_id=tenant_id,
            sku="RM-SEAL-KIT",
            name="Viton High-Temperature O-Ring & Pressure Packing Kit",
            category_id=raw_cat.id,
            uom_id=uom_ea.id,
            item_type="RAW_MATERIAL",
            standard_cost=Decimal("35.00"),
            moving_average_cost=Decimal("35.00"),
            list_price=Decimal("0.00"),
            lead_time_days=5,
            safety_stock=Decimal("100.0")
        )
        item_plungers = Item(
            tenant_id=tenant_id,
            sku="RM-CERAMIC-PLUNGER",
            name="Solid Zirconia Ceramic Plunger 28mm Precision Ground",
            category_id=raw_cat.id,
            uom_id=uom_ea.id,
            item_type="RAW_MATERIAL",
            standard_cost=Decimal("45.00"),
            moving_average_cost=Decimal("45.00"),
            list_price=Decimal("0.00"),
            lead_time_days=12,
            safety_stock=Decimal("60.0")
        )
        item_fasteners = Item(
            tenant_id=tenant_id,
            sku="RM-FASTENER-M12",
            name="Grade 12.9 High-Tensile Socket Cap Screws M12x60",
            category_id=raw_cat.id,
            uom_id=uom_ea.id,
            item_type="RAW_MATERIAL",
            standard_cost=Decimal("2.50"),
            moving_average_cost=Decimal("2.50"),
            list_price=Decimal("0.00"),
            lead_time_days=3,
            safety_stock=Decimal("500.0")
        )
        session.add_all([item_fg, item_sub, item_steel, item_motor, item_seals, item_plungers, item_fasteners])
        await session.flush()

        # 11. Multi-Tier Bills of Materials (BOM)
        print("-> Configuring Multi-Level Engineering BOM Recipes...")
        # Subassembly BOM
        sub_bom = BillOfMaterials(
            tenant_id=tenant_id,
            bom_number="BOM-SUB-VALVE-01",
            item_id=item_sub.id,
            quantity=Decimal("1.0"),
            uom_id=uom_ea.id,
            version="1.0",
            is_default=True,
            effective_from=date(2026, 1, 1)
        )
        session.add(sub_bom)
        await session.flush()

        session.add_all([
            BOMLine(tenant_id=tenant_id, bom_id=sub_bom.id, item_id=item_steel.id, quantity=Decimal("1.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("2.0")),
            BOMLine(tenant_id=tenant_id, bom_id=sub_bom.id, item_id=item_seals.id, quantity=Decimal("1.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("0.0")),
            BOMLine(tenant_id=tenant_id, bom_id=sub_bom.id, item_id=item_fasteners.id, quantity=Decimal("6.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("5.0")),
        ])

        # Top-Level Pump BOM
        top_bom = BillOfMaterials(
            tenant_id=tenant_id,
            bom_number="BOM-PUMP-500-01",
            item_id=item_fg.id,
            quantity=Decimal("1.0"),
            uom_id=uom_ea.id,
            version="1.0",
            is_default=True,
            effective_from=date(2026, 1, 1)
        )
        session.add(top_bom)
        await session.flush()

        session.add_all([
            BOMLine(tenant_id=tenant_id, bom_id=top_bom.id, item_id=item_sub.id, quantity=Decimal("1.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("0.0")),
            BOMLine(tenant_id=tenant_id, bom_id=top_bom.id, item_id=item_motor.id, quantity=Decimal("1.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("0.0")),
            BOMLine(tenant_id=tenant_id, bom_id=top_bom.id, item_id=item_plungers.id, quantity=Decimal("3.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("1.0")),
            BOMLine(tenant_id=tenant_id, bom_id=top_bom.id, item_id=item_fasteners.id, quantity=Decimal("12.0"), uom_id=uom_ea.id, scrap_percentage=Decimal("5.0")),
        ])

        # 12. Warehouses & Bin Locations
        print("-> Provisioning Warehouses & Storage Bin Coordinates...")
        plant_wh = Warehouse(tenant_id=tenant_id, code="PLANT-01", name="Main Industrial Manufacturing Plant", address="1000 Industrial Parkway, Buffalo, NY")
        dist_wh = Warehouse(tenant_id=tenant_id, code="WH-EAST", name="East Coast Distribution Center", address="450 Logistics Blvd, Newark, NJ")
        session.add_all([plant_wh, dist_wh])
        await session.flush()

        loc_raw = WarehouseLocation(tenant_id=tenant_id, warehouse_id=plant_wh.id, location_code="Z1-RAW-A01-B01", zone="Raw Materials", aisle="01", rack="01", shelf="01", bin="01")
        loc_wip = WarehouseLocation(tenant_id=tenant_id, warehouse_id=plant_wh.id, location_code="Z2-WIP-STAGE-01", zone="WIP Assembly", aisle="02", rack="01", shelf="01", bin="01")
        loc_fg = WarehouseLocation(tenant_id=tenant_id, warehouse_id=plant_wh.id, location_code="Z3-FG-BAY-01", zone="Finished Goods", aisle="03", rack="01", shelf="01", bin="01")
        session.add_all([loc_raw, loc_wip, loc_fg])
        await session.flush()

        # 13. Initial Stock Intake (Raw materials in stock)
        print("-> Receiving Opening Stock into Warehouses...")
        stock_intake_lines = [
            StockMovementLineCreate(item_id=item_steel.id, target_location_id=loc_raw.id, quantity=Decimal("150.0"), unit_cost=Decimal("110.00")),
            StockMovementLineCreate(item_id=item_motor.id, target_location_id=loc_raw.id, quantity=Decimal("40.0"), unit_cost=Decimal("650.00")),
            StockMovementLineCreate(item_id=item_seals.id, target_location_id=loc_raw.id, quantity=Decimal("300.0"), unit_cost=Decimal("35.00")),
            StockMovementLineCreate(item_id=item_plungers.id, target_location_id=loc_raw.id, quantity=Decimal("180.0"), unit_cost=Decimal("45.00")),
            StockMovementLineCreate(item_id=item_fasteners.id, target_location_id=loc_raw.id, quantity=Decimal("2000.0"), unit_cost=Decimal("2.50")),
            StockMovementLineCreate(item_id=item_fg.id, target_location_id=loc_fg.id, quantity=Decimal("25.0"), unit_cost=Decimal("1450.00")),
        ]
        mov_payload = StockMovementCreate(
            movement_type=MovementType.GOODS_RECEIPT,
            movement_date=date(2026, 1, 5),
            target_warehouse_id=plant_wh.id,
            reference="OPENING-STOCK-2026",
            remarks="Initial inventory load for plant startup",
            lines=stock_intake_lines
        )
        await StockMovementService.execute_movement(session, tenant_id, mov_payload, "system")

        # 14. Work Centers & Routings
        print("-> Setting up Work Centers and Machine Hourly Rates...")
        wc_cnc = WorkCenter(tenant_id=tenant_id, code="WC-CNC-01", name="5-Axis CNC Machining Center", work_center_type="MACHINE", hourly_rate=Decimal("85.00"), overhead_hourly_rate=Decimal("35.00"))
        wc_assm = WorkCenter(tenant_id=tenant_id, code="WC-ASSM-01", name="Precision Hydraulic Assembly Cell", work_center_type="ASSEMBLY", hourly_rate=Decimal("55.00"), overhead_hourly_rate=Decimal("20.00"))
        wc_test = WorkCenter(tenant_id=tenant_id, code="WC-TEST-01", name="High-Pressure Hydrostatic Test Cell", work_center_type="MACHINE", hourly_rate=Decimal("65.00"), overhead_hourly_rate=Decimal("25.00"))
        session.add_all([wc_cnc, wc_assm, wc_test])
        await session.flush()

        routing_fg = Routing(tenant_id=tenant_id, code="RT-PUMP-500", name="Triplex Pump Fabrication & Testing", item_id=item_fg.id, version="1.0")
        session.add(routing_fg)
        await session.flush()

        session.add_all([
            RoutingOperation(tenant_id=tenant_id, routing_id=routing_fg.id, sequence_number=10, work_center_id=wc_cnc.id, description="Manifold and Crankcase Precision CNC Milling", setup_time_mins=Decimal("30.0"), run_time_mins_per_unit=Decimal("45.0")),
            RoutingOperation(tenant_id=tenant_id, routing_id=routing_fg.id, sequence_number=20, work_center_id=wc_assm.id, description="Crankshaft, Ceramic Plunger & Seal Stack Assembly", setup_time_mins=Decimal("15.0"), run_time_mins_per_unit=Decimal("35.0")),
            RoutingOperation(tenant_id=tenant_id, routing_id=routing_fg.id, sequence_number=30, work_center_id=wc_test.id, description="5000 PSI Continuous Hydrostatic Proof & Flow Rate Test", setup_time_mins=Decimal("15.0"), run_time_mins_per_unit=Decimal("20.0")),
        ])

        # 15. Suppliers & Vendors
        print("-> Seeding Strategic Suppliers...")
        v1 = Vendor(
            tenant_id=tenant_id,
            code="VEND-001",
            name="Precision Alloy Forgings Corp",
            tax_identifier="EIN-45-8819210",
            payment_terms_days=30,
            credit_limit=Decimal("150000.00"),
            currency="USD",
            email="orders@precisionalloy.com",
            phone="+1-555-881-2291",
            address="700 Steel Mill Road, Pittsburgh, PA",
            ap_account_id=accounts_map["20100"].id,
            expense_account_id=accounts_map["12000"].id
        )
        v2 = Vendor(
            tenant_id=tenant_id,
            code="VEND-002",
            name="Titan Electric Industrial Motors Ltd",
            tax_identifier="EIN-92-3819201",
            payment_terms_days=45,
            credit_limit=Decimal("200000.00"),
            currency="USD",
            email="sales@titanmotors.com",
            phone="+1-555-442-9901",
            address="1200 Power Drive, Cleveland, OH",
            ap_account_id=accounts_map["20100"].id,
            expense_account_id=accounts_map["12000"].id
        )
        session.add_all([v1, v2])
        await session.flush()

        # 16. Customers
        print("-> Seeding Commercial Customers...")
        c1 = Customer(
            tenant_id=tenant_id,
            customer_number="CUST-001",
            name="Continental Petrochemical Refining Corp",
            tax_identifier="EIN-11-9988221",
            payment_terms_days=30,
            credit_limit=Decimal("250000.00"),
            current_balance=Decimal("0.0"),
            currency="USD",
            email="procurement@continentalrefining.com",
            phone="+1-555-331-9081",
            billing_address="5000 Energy Blvd, Houston, TX",
            shipping_address="Port Arthur Refinery Complex, Gate 4, Port Arthur, TX",
            ar_account_id=accounts_map["11000"].id,
            revenue_account_id=accounts_map["40100"].id
        )
        c2 = Customer(
            tenant_id=tenant_id,
            customer_number="CUST-002",
            name="Apex Marine & Heavy Offshore Engineering",
            tax_identifier="EIN-33-4411992",
            payment_terms_days=45,
            credit_limit=Decimal("500000.00"),
            current_balance=Decimal("0.0"),
            currency="USD",
            email="ap@apexmarineoffshore.com",
            phone="+1-555-772-1100",
            billing_address="100 Shipyard Way, Mobile, AL",
            shipping_address="Drydock Pier 9, Mobile, AL",
            ar_account_id=accounts_map["11000"].id,
            revenue_account_id=accounts_map["40100"].id
        )
        session.add_all([c1, c2])
        await session.flush()

        # 17. Departments & Employees
        print("-> Seeding Organizational Structure & Employees...")
        dept_exec = Department(tenant_id=tenant_id, code="EXEC", name="Executive Leadership")
        dept_eng = Department(tenant_id=tenant_id, code="ENG", name="Engineering & R&D")
        dept_mfg = Department(tenant_id=tenant_id, code="MFG", name="Plant Manufacturing & Assembly")
        dept_fin = Department(tenant_id=tenant_id, code="FIN", name="Finance & Accounting")
        session.add_all([dept_exec, dept_eng, dept_mfg, dept_fin])
        await session.flush()

        pos_ceo = JobPosition(tenant_id=tenant_id, code="CEO", title="Chief Executive Officer", department_id=dept_exec.id, grade_level="L1")
        pos_cfo = JobPosition(tenant_id=tenant_id, code="CFO", title="Chief Financial Officer", department_id=dept_fin.id, grade_level="L1")
        pos_lead_eng = JobPosition(tenant_id=tenant_id, code="LEAD_ENG", title="Principal Hydraulic Systems Engineer", department_id=dept_eng.id, grade_level="L4")
        pos_plant_mgr = JobPosition(tenant_id=tenant_id, code="PLANT_MGR", title="Manufacturing Operations Director", department_id=dept_mfg.id, grade_level="L2")
        pos_machinist = JobPosition(tenant_id=tenant_id, code="CNC_MACH", title="Lead CNC Precision Machinist", department_id=dept_mfg.id, grade_level="L5")
        session.add_all([pos_ceo, pos_cfo, pos_lead_eng, pos_plant_mgr, pos_machinist])
        await session.flush()

        emp1 = Employee(
            tenant_id=tenant_id,
            employee_number="EMP-001",
            first_name="Alexander",
            last_name="Vance",
            email="alexander.vance@apexdynamics.com",
            phone="+1-555-019-2831",
            date_of_joining=date(2022, 1, 1),
            department_id=dept_exec.id,
            job_position_id=pos_ceo.id,
            base_salary=Decimal("18500.00"),
            currency="USD"
        )
        emp2 = Employee(
            tenant_id=tenant_id,
            employee_number="EMP-002",
            first_name="Eleanor",
            last_name="Sterling",
            email="eleanor.sterling@apexdynamics.com",
            phone="+1-555-019-4492",
            date_of_joining=date(2022, 3, 1),
            department_id=dept_fin.id,
            job_position_id=pos_cfo.id,
            base_salary=Decimal("15000.00"),
            currency="USD"
        )
        emp3 = Employee(
            tenant_id=tenant_id,
            employee_number="EMP-003",
            first_name="Marcus",
            last_name="Kane",
            email="marcus.kane@apexdynamics.com",
            phone="+1-555-019-7711",
            date_of_joining=date(2022, 5, 1),
            department_id=dept_mfg.id,
            job_position_id=pos_plant_mgr.id,
            base_salary=Decimal("12500.00"),
            currency="USD"
        )
        emp4 = Employee(
            tenant_id=tenant_id,
            employee_number="EMP-004",
            first_name="Dr. Julian",
            last_name="Mercer",
            email="julian.mercer@apexdynamics.com",
            phone="+1-555-019-9031",
            date_of_joining=date(2023, 1, 15),
            department_id=dept_eng.id,
            job_position_id=pos_lead_eng.id,
            base_salary=Decimal("11000.00"),
            currency="USD"
        )
        emp5 = Employee(
            tenant_id=tenant_id,
            employee_number="EMP-005",
            first_name="Thomas",
            last_name="Hale",
            email="thomas.hale@apexdynamics.com",
            phone="+1-555-019-6612",
            date_of_joining=date(2023, 6, 1),
            department_id=dept_mfg.id,
            job_position_id=pos_machinist.id,
            base_salary=Decimal("7200.00"),
            currency="USD"
        )
        session.add_all([emp1, emp2, emp3, emp4, emp5])
        await session.commit()

    async with AsyncSessionLocal() as session:
        # 18. Sample Sales Order & Invoicing
        print("-> Executing Commercial Sales Order & Invoice for Continental Petrochemical...")
        inv_payload = SalesInvoiceCreate(
            customer_id=c1.id,
            invoice_date=date(2026, 1, 15),
            due_date=date(2026, 2, 14),
            currency="USD",
            lines=[
                SalesInvoiceLineCreate(
                    item_id=item_fg.id,
                    description="5000 PSI Hydraulic Triplex Pump Assembly",
                    quantity=Decimal("10.0"),
                    unit_price=Decimal("3200.00"),
                    discount_percent=Decimal("5.0"),
                    tax_amount=Decimal("2698.00"),
                    revenue_account_id=accounts_map["40100"].id
                )
            ]
        )
        inv = await SalesInvoiceService.create_invoice(session, tenant_id, inv_payload, admin_user.id)
        await SalesInvoiceService.post_sales_invoice(session, tenant_id, inv.id, admin_user.id)

        # 19. Sample Monthly Payroll Run
        print("-> Processing January 2026 Enterprise Payroll Run...")
        await PayrollCalculationService.execute_payroll_run(
            session,
            tenant_id,
            PayrollRunCreate(month=1, year=2026, run_date=date(2026, 1, 31)),
            cfo_user.id
        )

        # 20. Sample Production Order
        print("-> Scheduling Work Order for 15x Hydraulic Pumps...")
        wo_payload = ProductionOrderCreate(
            item_id=item_fg.id,
            bom_id=top_bom.id,
            routing_id=routing_fg.id,
            warehouse_id=plant_wh.id,
            planned_quantity=Decimal("15.0"),
            start_date=date(2026, 2, 1),
            due_date=date(2026, 2, 20)
        )
        await ProductionOrderService.create_production_order(session, tenant_id, wo_payload, ops_user.id)

        # 21. Sample Project Management Setup
        print("-> Creating Petrochemical R&D Engineering Project...")
        prj_payload = ProjectCreate(
            name="Next-Gen Subsea High-Pressure Pumping System R&D",
            customer_id=c1.id,
            manager_id=emp4.id,
            start_date=date(2026, 1, 10),
            end_date=date(2026, 6, 30),
            budget_amount=Decimal("450000.00"),
            billing_type="TIME_AND_MATERIALS"
        )
        prj = await ProjectService.create_project(session, tenant_id, prj_payload)
        await ProjectService.create_task(
            session,
            tenant_id,
            TaskCreate(
                project_id=prj.id,
                title="CFD Hydrodynamic Flow Simulation & Finite Element Stress Analysis",
                assigned_to_id=emp4.id,
                estimated_hours=Decimal("120.0"),
                priority="HIGH"
            )
        )

        await session.commit()

    print("==========================================================")
    print("[SUCCESS] NexERP Enterprise Database Seeded Successfully!")
    print(f"-> Tenant: Apex Dynamics Industrial Corp (ID: {tenant_id})")
    print("-> Admin Credentials: admin@apexdynamics.com / AdminPass123!")
    print("-> CFO Credentials:   cfo@apexdynamics.com   / FinancePass123!")
    print("-> Ops Credentials:   operations@apexdynamics.com / OpsPass123!")
    print("==========================================================")


if __name__ == "__main__":
    asyncio.run(seed_enterprise_data())
