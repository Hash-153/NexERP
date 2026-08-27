"""
Global E-Invoicing & PEPPOL BIS 3.0 Enums.
"""
import enum

class EInvoiceStandard(str, enum.Enum):
    PEPPOL_BIS_BILLING_3 = "PEPPOL_BIS_BILLING_3"  # Pan-European Public Procurement On-Line
    ZUGFERD_FACTUR_X = "ZUGFERD_FACTUR_X"          # Germany / France PDF/A-3 hybrid
    ITALIAN_SDI_FATTURAPA = "ITALIAN_SDI_FATTURAPA"# Italy Sistema di Interscambio
    MEXICAN_CFDI_40 = "MEXICAN_CFDI_40"            # Mexico SAT Comprobante Fiscal Digital
    BRAZILIAN_NFE_55 = "BRAZILIAN_NFE_55"          # Brazil Nota Fiscal Eletronica
    INDIAN_E_INVOICE_IRN = "INDIAN_E_INVOICE_IRN"  # India GST e-Invoice Invoice Reference Number

class TransmissionStatus(str, enum.Enum):
    GENERATED = "GENERATED"
    VALIDATED_SCHEMATRON = "VALIDATED_SCHEMATRON"
    TRANSMITTED_ACCESS_POINT = "TRANSMITTED_ACCESS_POINT"
    ACKNOWLEDGED_POSITIVE = "ACKNOWLEDGED_POSITIVE"
    REJECTED_ERROR = "REJECTED_ERROR"
