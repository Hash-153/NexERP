"""
Enterprise Document Generator & Printing Subsystem.
Produces formatted HTML / PDF / Print payloads for Commercial Invoices, Purchase Orders, Packing Slips, and Pick Tickets.
"""
from decimal import Decimal
from typing import Dict, Any, List

class DocumentTemplatingService:
    @staticmethod
    def render_commercial_invoice_html(invoice_data: Dict[str, Any]) -> str:
        lines_html = ""
        for line in invoice_data.get("lines", []):
            lines_html += f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 10px; font-family: monospace;">{line.get('sku', '')}</td>
                <td style="padding: 10px;">{line.get('description', '')}</td>
                <td style="padding: 10px; text-align: right;">{line.get('quantity', 0):,.2f}</td>
                <td style="padding: 10px; text-align: right;">${line.get('unit_price', 0):,.2f}</td>
                <td style="padding: 10px; text-align: right; font-weight: bold;">${line.get('extended_total', 0):,.2f}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Commercial Invoice - {invoice_data.get('invoice_number', '')}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1f2937; margin: 40px; }}
                .header {{ display: flex; justify-content: space-between; border-bottom: 3px solid #1e3a8a; padding-bottom: 20px; }}
                .logo-title {{ font-size: 26px; font-weight: 800; color: #1e3a8a; }}
                .meta-table {{ margin-top: 20px; width: 100%; }}
                .meta-table td {{ padding: 6px; vertical-align: top; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
                .items-table th {{ background-color: #f3f4f6; padding: 10px; text-align: left; font-size: 13px; text-transform: uppercase; }}
                .totals-box {{ margin-top: 20px; margin-left: auto; width: 320px; border-collapse: collapse; }}
                .totals-box td {{ padding: 6px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <div class="logo-title">{invoice_data.get('tenant_name', 'NexERP Enterprise')}</div>
                    <div>100 Enterprise Way, Suite 400</div>
                    <div>San Francisco, CA 94105, USA</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 22px; font-weight: bold; color: #4b5563;">COMMERCIAL INVOICE</div>
                    <div><strong>Invoice #:</strong> {invoice_data.get('invoice_number', '')}</div>
                    <div><strong>Date:</strong> {invoice_data.get('invoice_date', '')}</div>
                    <div><strong>Due Date:</strong> {invoice_data.get('due_date', '')}</div>
                </div>
            </div>

            <table class="meta-table">
                <tr>
                    <td style="width: 50%;">
                        <strong>Billed To:</strong><br>
                        {invoice_data.get('customer_name', '')}<br>
                        {invoice_data.get('customer_address', '')}<br>
                        Tax ID / VAT: {invoice_data.get('customer_tax_id', 'N/A')}
                    </td>
                    <td style="width: 50%;">
                        <strong>Payment Terms:</strong> {invoice_data.get('payment_terms', 'Net 30')}<br>
                        <strong>Currency:</strong> {invoice_data.get('currency', 'USD')}<br>
                        <strong>Purchase Order Ref:</strong> {invoice_data.get('po_reference', 'N/A')}
                    </td>
                </tr>
            </table>

            <table class="items-table">
                <thead>
                    <tr>
                        <th style="width: 15%;">SKU / Item</th>
                        <th style="width: 45%;">Description</th>
                        <th style="width: 12%; text-align: right;">Qty</th>
                        <th style="width: 13%; text-align: right;">Unit Price</th>
                        <th style="width: 15%; text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {lines_html}
                </tbody>
            </table>

            <table class="totals-box">
                <tr>
                    <td>Subtotal:</td>
                    <td style="text-align: right;">${invoice_data.get('subtotal', 0):,.2f}</td>
                </tr>
                <tr>
                    <td>Sales Tax / VAT:</td>
                    <td style="text-align: right;">${invoice_data.get('tax_total', 0):,.2f}</td>
                </tr>
                <tr style="border-top: 2px solid #1f2937; font-size: 16px; font-weight: bold;">
                    <td>Total Due:</td>
                    <td style="text-align: right; color: #1e3a8a;">${invoice_data.get('total_amount', 0):,.2f} {invoice_data.get('currency', 'USD')}</td>
                </tr>
            </table>

            <div style="margin-top: 60px; padding: 15px; background-color: #f8fafc; border-left: 4px solid #3b82f6; font-size: 12px; color: #64748b;">
                <strong>Remittance Instructions:</strong> Wire transfer to Bank of America, Routing #121000358, Account #4430192831, SWIFT: BOFAUS3N. Please include invoice number in wire details.
            </div>
        </body>
        </html>
        """
        return html
