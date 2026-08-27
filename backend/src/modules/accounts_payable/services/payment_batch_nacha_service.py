"""
NexERP Banking & NACHA ACH / ISO 20022 Electronic Payment File Formatter.
Generates compliant 94-character fixed-width NACHA CCD+ payment files
for Automated Clearing House (ACH) electronic vendor disbursements.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List


class NACHAPaymentFileService:
    """
    Electronic Funds Transfer (EFT) NACHA File Generator.
    """

    @classmethod
    def generate_nacha_ach_file(
        cls,
        immediate_destination_routing: str,
        immediate_origin_company_id: str,
        company_name: str,
        company_discretionary_data: str,
        payments: List[Dict]
    ) -> str:
        """
        Build 94-character fixed record NACHA ACH payment batch file.
        """
        now = datetime.now()
        file_creation_date = now.strftime("%y%m%d")
        file_creation_time = now.strftime("%H%M")
        eff_entry_date = (payments[0].get("settlement_date") or date.today()).strftime("%y%m%d") if payments else date.today().strftime("%y%m%d")

        dest = immediate_destination_routing.replace("-", "").strip().ljust(10)[:10]
        orig = immediate_origin_company_id.strip().ljust(10)[:10]
        comp_name = company_name.upper().ljust(16)[:16]

        lines = []

        # 1. File Header Record (Record Type 1)
        file_header = f"101 {dest}{orig}{file_creation_date}{file_creation_time}A094101{dest}{comp_name}NEXERP_ACH "
        lines.append(file_header[:94].ljust(94))

        # 2. Batch Header Record (Record Type 5)
        batch_header = f"5200{comp_name}{company_discretionary_data.ljust(20)[:20]}{orig}CCDVENDOR PMT{eff_entry_date}   100000010000001"
        lines.append(batch_header[:94].ljust(94))

        total_debit = Decimal("0.0")
        total_credit = Decimal("0.0")
        entry_hash = 0

        # 3. Entry Detail Records (Record Type 6)
        for idx, pmt in enumerate(payments, start=1):
            routing = str(pmt["vendor_bank_routing"]).replace("-", "").strip()[:9].rjust(9, "0")
            acc_num = str(pmt["vendor_bank_account"]).strip()[:17].ljust(17)
            amt_cents = int(Decimal(str(pmt["amount"])) * 100)
            total_credit += Decimal(str(pmt["amount"]))
            vendor_name = str(pmt["vendor_name"]).upper().ljust(22)[:22]
            trace_num = f"00000001{idx:07d}"

            entry_hash += int(routing[:8])

            entry_line = f"622{routing}{acc_num}{amt_cents:010d}{pmt.get('vendor_id', '')[:15].ljust(15)}{vendor_name}  0{trace_num}"
            lines.append(entry_line[:94].ljust(94))

        # 4. Batch Control Record (Record Type 8)
        hash_str = str(entry_hash)[-10:].rjust(10, "0")
        credit_cents = int(total_credit * 100)
        batch_control = f"8200{len(payments):06d}{hash_str}000000000000{credit_cents:012d}{orig}                         0000001"
        lines.append(batch_control[:94].ljust(94))

        # 5. File Control Record (Record Type 9)
        block_count = (len(lines) + 1 + 9) // 10
        file_control = f"9000001{block_count:06d}{len(payments):08d}{hash_str}000000000000{credit_cents:012d}                                       "
        lines.append(file_control[:94].ljust(94))

        return "\n".join(lines)
