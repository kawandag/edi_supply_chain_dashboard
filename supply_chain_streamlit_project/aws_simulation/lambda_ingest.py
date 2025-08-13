import boto3, os, json
from urllib.parse import unquote_plus

s3 = boto3.client('s3')

def parse_line(line: str):
    return line.strip().split('|')

def to_obj(parts):
    t = parts[0]
    if t == '810':
        _, invoice_id, partner_id, partner_name, po_id, invoice_date, amount, terms = parts
        return {"type":"invoice","invoice_id":invoice_id,"partner_id":partner_id,"partner_name":partner_name,
                "po_id":po_id,"invoice_date":invoice_date,"amount":float(amount),"terms":int(terms)}
    if t == '820':
        _, payment_id, partner_id, partner_name, invoice_id, payment_date, amount = parts
        return {"type":"payment","payment_id":payment_id,"partner_id":partner_id,"partner_name":partner_name,
                "invoice_id":invoice_id,"payment_date":payment_date,"amount":float(amount)}
    return {"type":"unknown","raw":parts}

def lambda_handler(event, context):
    for rec in event.get('Records', []):
        bucket = rec['s3']['bucket']['name']
        key = unquote_plus(rec['s3']['object']['key'])
        body = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8').strip()
        obj = to_obj(parse_line(body))
        out_key = f"processed/{os.path.splitext(os.path.basename(key))[0]}.json"
        s3.put_object(Bucket=bucket, Key=out_key, Body=json.dumps(obj).encode('utf-8'))
        print(f"Processed {key} -> {out_key}")
    return {"ok": True}
