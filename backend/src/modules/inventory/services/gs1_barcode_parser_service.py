"""
NexERP GS1-128 Barcode Application Identifier (AI) Parser Engine.
Parses standard concatenated GS1 barcodes:
- (01) GTIN - Global Trade Item Number (14 digits)
- (10) Batch / Lot Number (Alphanumeric up to 20 chars)
- (17) Expiration Date (YYMMDD format)
- (21) Serial Number (Alphanumeric up to 20 chars)
- (310x) Net Weight in Kilograms (Variable decimal).
"""

import re
from datetime import date
from decimal import Decimal
from typing import Dict, Optional


class GS1BarcodeParserService:
    """
    GS1-128 / GS1 DataMatrix 2D Barcode Decoder Service.
    """

    @classmethod
    def parse_gs1_barcode(cls, raw_barcode_string: str) -> Dict:
        """
        Extract structured logistics attributes from bracketed or raw GS1 strings.
        Example format: '(01)00850012345678(17)261231(10)LOT-8891(21)SN-44120'
        """
        # Normalize by extracting bracketed AIs or sequential patterns
        parsed_data = {
            "raw_string": raw_barcode_string,
            "gtin_01": None,
            "lot_number_10": None,
            "expiration_date_17": None,
            "serial_number_21": None,
            "net_weight_kg_3102": None,
            "is_valid_gs1": False
        }

        # 1. GTIN (01) - 14 digits
        gtin_match = re.search(r'(?:\(01\)|01)(\d{14})', raw_barcode_string)
        if gtin_match:
            parsed_data["gtin_01"] = gtin_match.group(1)

        # 2. Expiration Date (17) - 6 digits (YYMMDD)
        exp_match = re.search(r'(?:\(17\)|17)(\d{6})', raw_barcode_string)
        if exp_match:
            raw_exp = exp_match.group(1)
            yy = int(raw_exp[0:2]) + 2000
            mm = int(raw_exp[2:4])
            dd = int(raw_exp[4:6])
            try:
                parsed_data["expiration_date_17"] = date(yy, mm, dd).isoformat()
            except ValueError:
                parsed_data["expiration_date_17"] = None

        # 3. Lot / Batch (10)
        lot_match = re.search(r'(?:\(10\)|10)([A-Za-z0-9\-_]+?)(?=\(\d{2}\)|$)', raw_barcode_string)
        if lot_match:
            parsed_data["lot_number_10"] = lot_match.group(1)

        # 4. Serial Number (21)
        sn_match = re.search(r'(?:\(21\)|21)([A-Za-z0-9\-_]+?)(?=\(\d{2}\)|$)', raw_barcode_string)
        if sn_match:
            parsed_data["serial_number_21"] = sn_match.group(1)

        # 5. Net Weight (3102) - 6 digits (e.g. 3102001500 -> 15.00 kg)
        wt_match = re.search(r'(?:\(3102\)|3102)(\d{6})', raw_barcode_string)
        if wt_match:
            raw_wt = Decimal(wt_match.group(1)) / Decimal("100.0")
            parsed_data["net_weight_kg_3102"] = float(raw_wt)

        # Flag valid if at least GTIN or Lot found
        parsed_data["is_valid_gs1"] = bool(parsed_data["gtin_01"] or parsed_data["lot_number_10"])

        return parsed_data
