"""
NexERP Auth Module Enums and Standard Permission Constants.
"""

from enum import Enum


class StandardRoles(str, Enum):
    SUPER_ADMIN = "SuperAdmin"
    CHIEF_EXECUTIVE = "CEO"
    CHIEF_FINANCIAL_OFFICER = "CFO"
    FINANCE_MANAGER = "FinanceManager"
    ACCOUNTANT = "Accountant"
    SUPPLY_CHAIN_MANAGER = "SupplyChainManager"
    PROCUREMENT_OFFICER = "ProcurementOfficer"
    WAREHOUSE_MANAGER = "WarehouseManager"
    SALES_DIRECTOR = "SalesDirector"
    SALES_REPRESENTATIVE = "SalesRepresentative"
    PRODUCTION_MANAGER = "ProductionManager"
    SHOP_FLOOR_OPERATOR = "ShopFloorOperator"
    QUALITY_INSPECTOR = "QualityInspector"
    HR_MANAGER = "HRManager"
    PROJECT_MANAGER = "ProjectManager"
    AUDITOR = "Auditor"


SYSTEM_PERMISSIONS = [
    # Auth & System Admin
    ("admin:all", "Admin", "Full unrestricted administrative access to entire system"),
    ("auth:users:manage", "Admin", "Create, update, and deactivate user accounts"),
    ("auth:roles:manage", "Admin", "Configure roles and assign permissions"),
    ("core:audit:view", "Admin", "Inspect forensic audit logs and change history"),

    # Financials & General Ledger
    ("financials:account:view", "Financials", "View Chart of Accounts and balances"),
    ("financials:account:manage", "Financials", "Create and modify accounts in COA"),
    ("financials:journal:view", "Financials", "View journal entries and ledgers"),
    ("financials:journal:create", "Financials", "Create and draft journal vouchers"),
    ("financials:journal:post", "Financials", "Post and finalize journal entries to general ledger"),
    ("financials:period:close", "Financials", "Close and lock fiscal periods"),
    ("financials:reports:view", "Financials", "Generate Balance Sheet, P&L, and Cash Flow statements"),
    ("financials:assets:manage", "Financials", "Manage fixed assets and run depreciation schedules"),

    # Accounts Payable
    ("ap:vendors:view", "AccountsPayable", "View vendor directory and profiles"),
    ("ap:vendors:manage", "AccountsPayable", "Create and update vendor profiles"),
    ("ap:bills:view", "AccountsPayable", "View vendor bills and open balances"),
    ("ap:bills:create", "AccountsPayable", "Create and record vendor bills"),
    ("ap:bills:approve", "AccountsPayable", "Approve vendor bills for disbursement"),
    ("ap:payments:process", "AccountsPayable", "Execute payment runs and disburse funds"),

    # Accounts Receivable
    ("ar:customers:view", "AccountsReceivable", "View customer directory and accounts"),
    ("ar:customers:manage", "AccountsReceivable", "Create and update customer profiles"),
    ("ar:invoices:view", "AccountsReceivable", "View customer sales invoices"),
    ("ar:invoices:create", "AccountsReceivable", "Create and issue sales invoices"),
    ("ar:receipts:record", "AccountsReceivable", "Record and allocate customer payments"),
    ("ar:dunning:manage", "AccountsReceivable", "Execute dunning cycles and credit hold actions"),

    # Inventory & WMS
    ("inventory:items:view", "Inventory", "View items, inventory quantities, and locations"),
    ("inventory:items:manage", "Inventory", "Create and update item master catalog"),
    ("inventory:movements:create", "Inventory", "Record goods receipt, issue, and transfers"),
    ("inventory:valuation:view", "Inventory", "Inspect FIFO lot layers and inventory valuation"),
    ("inventory:cycle_count:manage", "Inventory", "Execute physical cycle counts and approve variances"),

    # Procurement & SCM
    ("procurement:requisitions:create", "Procurement", "Create purchase requisitions"),
    ("procurement:requisitions:approve", "Procurement", "Approve purchase requisitions"),
    ("procurement:orders:create", "Procurement", "Create and issue Purchase Orders"),
    ("procurement:orders:approve", "Procurement", "Approve Purchase Orders"),
    ("procurement:receipts:record", "Procurement", "Record Goods Receipt Notes (GRN)"),

    # Sales & CRM
    ("sales:leads:manage", "Sales", "Manage sales leads and opportunities"),
    ("sales:quotes:create", "Sales", "Create and send sales quotations"),
    ("sales:orders:create", "Sales", "Create and confirm customer sales orders"),
    ("sales:fulfillment:manage", "Sales", "Pick, pack, and generate delivery shipments"),

    # Manufacturing & MRP
    ("manufacturing:bom:manage", "Manufacturing", "Create and maintain multi-level Bill of Materials"),
    ("manufacturing:work_centers:manage", "Manufacturing", "Configure work centers and routings"),
    ("manufacturing:orders:manage", "Manufacturing", "Create, schedule, and release Production Orders"),
    ("manufacturing:mrp:run", "Manufacturing", "Execute MRP planning calculation runs"),
    ("manufacturing:shopfloor:log", "Manufacturing", "Log job ticket labor and machine time"),

    # Quality Control
    ("quality:plans:manage", "QualityControl", "Configure quality inspection criteria and AQL plans"),
    ("quality:inspections:execute", "QualityControl", "Execute quality inspection tests and record results"),
    ("quality:ncr:manage", "QualityControl", "File and resolve Non-Conformance Reports (NCR) and CAPA"),

    # Human Resources & Payroll
    ("hr:employees:view", "HumanResources", "View employee directory"),
    ("hr:employees:manage", "HumanResources", "Create, update, and manage employee records"),
    ("hr:leaves:manage", "HumanResources", "Manage leave requests, balances, and policies"),
    ("hr:attendance:manage", "HumanResources", "Record attendance punches and shift rosters"),
    ("hr:payroll:view", "HumanResources", "View payroll runs and employee payslips"),
    ("hr:payroll:execute", "HumanResources", "Execute monthly payroll calculation batch"),

    # Projects
    ("projects:projects:manage", "Projects", "Create and schedule projects, WBS tasks, and milestones"),
    ("projects:timesheets:log", "Projects", "Log employee project timesheets"),
    ("projects:timesheets:approve", "Projects", "Approve billable timesheets for invoicing"),
]
