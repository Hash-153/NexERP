"""
Multi-Processor Enterprise Payment Gateway & ISO 20022 SEPA XML Subsystem.
"""
from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime, date

class PaymentGatewayProcessor:
    @staticmethod
    def generate_sepa_pain_001_xml(batch_reference: str, debtor_iban: str, debtor_bic: str, payments: List[Dict[str, Any]]) -> str:
        """Generates ISO 20022 pain.001.001.03 Credit Transfer initiation message."""
        total_sum = sum(Decimal(str(p.get("amount", 0))) for p in payments)
        tx_nodes = ""
        
        for idx, p in enumerate(payments, start=1):
            tx_nodes += f"""
            <CdtTrfTxInf>
                <PmtId>
                    <EndToEndId>{p.get('end_to_end_id', f'E2E-{batch_reference}-{idx}')}</EndToEndId>
                </PmtId>
                <Amt>
                    <InstdAmt Ccy="{p.get('currency', 'EUR')}">{Decimal(str(p.get('amount', 0))):.2f}</InstdAmt>
                </Amt>
                <CdtrAgt>
                    <FinInstnId>
                        <BIC>{p.get('creditor_bic', '')}</BIC>
                    </FinInstnId>
                </CdtrAgt>
                <Cdtr>
                    <Nm>{p.get('creditor_name', '')}</Nm>
                </Cdtr>
                <CdtrAcct>
                    <Id>
                        <IBAN>{p.get('creditor_iban', '')}</IBAN>
                    </Id>
                </CdtrAcct>
                <RmtInf>
                    <Ustrd>{p.get('remittance_info', '')}</Ustrd>
                </RmtInf>
            </CdtTrfTxInf>
            """

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>{batch_reference}</MsgId>
            <CreDtTm>{datetime.utcnow().isoformat()}</CreDtTm>
            <NbOfTxs>{len(payments)}</NbOfTxs>
            <CtrlSum>{total_sum:.2f}</CtrlSum>
            <InitgPty>
                <Nm>NexERP Enterprise Treasury</Nm>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMT-{batch_reference}</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <ReqdExctnDt>{date.today().isoformat()}</ReqdExctnDt>
            <Dbtr>
                <Nm>Apex Dynamics Enterprise Corp</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>{debtor_iban}</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BIC>{debtor_bic}</BIC>
                </FinInstnId>
            </DbtrAgt>
            {tx_nodes}
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""
        return xml

    @staticmethod
    def generate_nacha_ach_file(company_id: str, company_name: str, origin_dfi: str, batch_id: str, entries: List[Dict[str, Any]]) -> str:
        """Generates standard 94-character fixed width NACHA ACH payment batch file."""
        lines = []
        # File Header (Record 1)
        now_str = datetime.now().strftime("%y%m%d%H%M")
        file_header = f"101 {origin_dfi[:9]:<9} {company_id[:10]:<10}{now_str}A094101{company_name[:23]:<23}NEXERP TREASURY        "
        lines.append(file_header[:94])
        
        # Batch Header (Record 5)
        batch_header = f"5200{company_name[:16]:<16}PAYROLL       {company_id[:10]:<10}CCD{datetime.now().strftime('%y%m%d')}{datetime.now().strftime('%y%m%d')}   1{origin_dfi[:8]}0000001"
        lines.append(batch_header[:94])
        
        total_credit = Decimal("0.0")
        entry_hash = 0
        
        for idx, entry in enumerate(entries, start=1):
            routing = entry.get("routing_number", "121000358")[:8]
            entry_hash += int(routing)
            amt = Decimal(str(entry.get("amount", "0.00")))
            total_credit += amt
            amt_cents = int(amt * 100)
            account_num = entry.get("account_number", "00000000")[:17]
            receiver_name = entry.get("receiver_name", "Vendor Payee")[:22]
            
            # Entry Detail (Record 6)
            detail = f"622{routing[:8]}{routing[7:8]}{account_num:<17}{amt_cents:010d}{entry.get('identification', f'ID{idx}'):<15}{receiver_name:<22}  0{origin_dfi[:8]}{idx:07d}"
            lines.append(detail[:94])
            
        # Batch Control (Record 8)
        hash_str = str(entry_hash)[-10:].zfill(10)
        total_cents = int(total_credit * 100)
        batch_control = f"8200{len(entries):06d}{hash_str}000000000000{total_cents:012d}{company_id[:10]:<10}                         {origin_dfi[:8]}0000001"
        lines.append(batch_control[:94])
        
        # File Control (Record 9)
        file_control = f"9000001{len(lines) + 1:06d}{len(entries):08d}{hash_str}000000000000{total_cents:012d}                                       "
        lines.append(file_control[:94])
        
        return "\n".join(lines)
