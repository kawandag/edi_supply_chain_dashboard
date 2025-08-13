import pandas as pd
from dateutil import parser

def parse_edi_810(file_path: str) -> pd.DataFrame:
    records = []
    with open(file_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    current = {}
    for ln in lines:
        parts = ln.split("*")
        tag = parts[0]
        if tag == "BIG":
            current["invoice_date"] = parser.parse(parts[1]).date()
            current["invoice_number"] = parts[2]
        elif tag == "N1" and len(parts) > 2 and parts[1] == "BY":
            current["payer_id"] = parts[2]
        elif tag == "ITD":
            # parts: ITD*01*terms*amount
            current["terms"] = int(parts[2])
            current["amount"] = float(parts[3])
            records.append(current)
            current = {}
    return pd.DataFrame.from_records(records)

def parse_edi_820(file_path: str) -> pd.DataFrame:
    records = []
    with open(file_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    current = {}
    for ln in lines:
        parts = ln.split("*")
        tag = parts[0]
        if tag == "BPR":
            current["payment_amount"] = float(parts[1])
            current["payment_date"] = parser.parse(parts[3]).date()
        elif tag == "N1" and len(parts) > 2 and parts[1] == "BY":
            current["payer_id"] = parts[2]
        elif tag == "RMR":
            # RMR*IV<invoice_number>*amount
            current["invoice_number"] = parts[1].replace("IV", "")
            records.append(current)
            current = {}
    return pd.DataFrame.from_records(records)
