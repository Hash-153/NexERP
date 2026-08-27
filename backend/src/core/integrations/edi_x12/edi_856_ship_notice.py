"""
ANSI ASC X12 Transaction Set 856 (Ship Notice / Manifest - ASN) Generator.
"""
from typing import Dict, Any

class EDI856AdvanceShipNoticeGenerator:
    @staticmethod
    def generate_x12_856_string(asn_data: Dict[str, Any]) -> str:
        segments = []
        segments.append("ISA*00*          *00*          *ZZ*NEXERP         *ZZ*PARTNER        *260301*1200*U*00401*000000001*0*P*>")
        segments.append("GS*SH*NEXERP*PARTNER*20260301*1200*1*X*004010")
        segments.append(f"ST*856*0001")
        segments.append(f"BSN*00*{asn_data.get('asn_number', 'ASN001')}*20260301*1200*0001")
        segments.append(f"HL*1**S")  # Shipment level
        segments.append(f"TD1*CTN25*{asn_data.get('total_cartons', 1)}")
        segments.append(f"TD5*B*02*FEDX*M*{asn_data.get('carrier_name', 'FedEx')}")
        segments.append(f"REF*BM*{asn_data.get('bol_number', 'BOL1000')}")
        segments.append(f"HL*2*1*O")  # Order level
        segments.append(f"PRF*{asn_data.get('po_number', 'PO9999')}")
        segments.append(f"HL*3*2*I")  # Item level
        segments.append(f"LIN*1*VP*{asn_data.get('sku', 'SKU-001')}")
        segments.append(f"SN1*1*{asn_data.get('quantity', 100)}*EA")
        segments.append("SE*12*0001")
        segments.append("GE*1*1")
        segments.append("IEA*1*000000001")
        return "~".join(segments) + "~"
