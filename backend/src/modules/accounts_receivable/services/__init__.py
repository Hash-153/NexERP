"""
NexERP Accounts Receivable Module Services.
"""

from .sales_invoice_service import SalesInvoiceService
from .payment_receipt_service import PaymentReceiptService
from .customer_service import CustomerService
from .dunning_service import DunningService
from .ar_aging_service import ARAgingService
from .dso_aging_buckets_service import ARAgingAnalysisService
from .credit_scoring_engine_service import CustomerCreditScoringService
from .dunning_escalation_service import DunningEscalationService

CustomerInvoiceService = SalesInvoiceService
DebtCollectionService = DunningService

__all__ = [
    "SalesInvoiceService",
    "CustomerInvoiceService",
    "PaymentReceiptService",
    "CustomerService",
    "DunningService",
    "ARAgingService",
    "ARAgingAnalysisService",
    "CustomerCreditScoringService",
    "DebtCollectionService",
    "DSOAgingBucketsService",
    "CreditScoringEngineService",
    "DunningEscalationService",
]
