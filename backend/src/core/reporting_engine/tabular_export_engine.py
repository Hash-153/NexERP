"""
Tabular Data Streaming & Export Serialization Engine (CSV, TSV, JSONL).
"""
import io
import csv
from decimal import Decimal
from typing import List, Dict, Any, Generator

class TabularExportEngine:
    @staticmethod
    def stream_csv(records: List[Dict[str, Any]], fieldnames: List[str]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in records:
            cleaned_row = {}
            for k, v in row.items():
                if isinstance(v, Decimal):
                    cleaned_row[k] = float(v)
                elif isinstance(v, (list, dict)):
                    cleaned_row[k] = str(v)
                else:
                    cleaned_row[k] = v
            writer.writerow(cleaned_row)
        return output.getvalue()
