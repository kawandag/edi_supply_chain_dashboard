from faker import Faker
from datetime import datetime, timedelta
import random
from pathlib import Path

fake = Faker()

def generate_edi_810(num_records=100):
    lines = []
    today = datetime.today().date()
    for _ in range(num_records):
        invoice_number = fake.unique.random_int(100000, 999999)
        inv_date = today - timedelta(days=random.randint(15, 120))
        amount = round(random.uniform(200, 20000), 2)
        payer_id = random.randint(10000, 99999)
        po = random.randint(1000, 9999)
        lines += [
            f"ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     *{inv_date.strftime('%y%m%d')}*{invoice_number}*U*00401*000000001*0*T*:",
            f"BIG*{inv_date.strftime('%Y%m%d')}*{invoice_number}**PO{po}",
            f"N1*BY*{payer_id}",
            f"ITD*01*{random.choice([15,30,45,60])}*{amount}"
        ]
    return "\n".join(lines)

def generate_edi_820(num_records=80):
    lines = []
    today = datetime.today().date()
    for _ in range(num_records):
        payment_date = today - timedelta(days=random.randint(1, 60))
        amount = round(random.uniform(200, 20000), 2)
        payer_id = random.randint(10000, 99999)
        invoice_number = random.randint(100000, 999999)
        lines += [
            f"ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     *{payment_date.strftime('%y%m%d')}*{invoice_number}*U*00401*000000002*0*T*:",
            f"BPR*{amount}*USD*{payment_date.strftime('%Y%m%d')}",
            f"N1*BY*{payer_id}",
            f"RMR*IV{invoice_number}*{amount}"
        ]
    return "\n".join(lines)

if __name__ == "__main__":
    Path("sample_data").mkdir(exist_ok=True)
    Path("sample_data/invoice_810.edi").write_text(generate_edi_810())
    Path("sample_data/payment_820.edi").write_text(generate_edi_820())
    print("Mock EDI files written to sample_data/.")
