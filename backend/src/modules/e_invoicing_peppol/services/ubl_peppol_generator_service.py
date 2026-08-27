"""
OASIS UBL 2.1 / PEPPOL BIS Billing 3.0 XML Synthesis Engine.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any

from backend.src.core.audit import AuditService
from ..models import EInvoiceTransmissionRecord
from ..schemas import EInvoiceGenerateRequest

class UBLPeppolGeneratorService:
    @staticmethod
    def generate_ubl_xml(req: EInvoiceGenerateRequest) -> str:
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0</cbc:CustomizationID>
    <cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID>
    <cbc:ID>{req.invoice_number}</cbc:ID>
    <cbc:IssueDate>{req.issue_date.isoformat()}</cbc:IssueDate>
    <cbc:DueDate>{req.due_date.isoformat()}</cbc:DueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>{req.currency}</cbc:DocumentCurrencyCode>
    
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cbc:EndpointID schemeID="9930">{req.seller_vat_id}</cbc:EndpointID>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>Apex Dynamics Enterprise Corp</cbc:RegistrationName>
                <cbc:CompanyID>{req.seller_vat_id}</cbc:CompanyID>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cbc:EndpointID schemeID="{req.buyer_endpoint_scheme}">{req.buyer_endpoint_id}</cbc:EndpointID>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>Customer Enterprise Recipient</cbc:RegistrationName>
                <cbc:CompanyID>{req.buyer_vat_id}</cbc:CompanyID>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingCustomerParty>
    
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="{req.currency}">{req.tax_amount:.2f}</cbc:TaxAmount>
    </cac:TaxTotal>
    
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="{req.currency}">{(req.total_amount - req.tax_amount):.2f}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="{req.currency}">{(req.total_amount - req.tax_amount):.2f}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="{req.currency}">{req.total_amount:.2f}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="{req.currency}">{req.total_amount:.2f}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
</Invoice>"""
        return xml
