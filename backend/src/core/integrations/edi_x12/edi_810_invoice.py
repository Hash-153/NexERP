"""
ANSI ASC X12 Transaction Set 810 (Commercial Invoice) Generator.
"""
from typing import Dict, Any

class EDI810InvoiceGenerator:
    @staticmethod
    def generate_x12_810_string(inv_data: Dict[str, Any]) -> str:
        segments = []
        segments.append("ISA*00*          *00*          *ZZ*NEXERP         *ZZ*PARTNER        *260301*1200*U*00401*000000001*0*P*>")
        segments.append("GS*IN*NEXERP*PARTNER*20260301*1200*1*X*004010")
        segments.append("ST*810*0001")
        segments.append(f"BIG*20260301*{inv_data.get('invoice_number', 'INV001')}*20260301*{inv_data.get('po_number', 'PO001')}")
        segments.append(f"ITD*01*3*2**10**30")  # Net 30, 2% 10 days
        segments.append(f"TDS*{int(float(inv_data.get('total_amount', 0)) * 100)}")
        segments.append("SE*6*0001")
        segments.append("GE*1*1")
        segments.append("IEA*1*000000001")
        return "~".join(segments) + "~"
