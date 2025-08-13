CREATE SCHEMA IF NOT EXISTS supply_chain;
CREATE TABLE IF NOT EXISTS supply_chain.invoices (
  invoice_id VARCHAR(64) PRIMARY KEY,
  partner_id VARCHAR(32),
  partner_name VARCHAR(256),
  po_id VARCHAR(64),
  invoice_date DATE,
  amount DOUBLE PRECISION,
  terms INTEGER,
  payment_date DATE,
  days_to_pay INTEGER,
  is_late BOOLEAN
);
CREATE TABLE IF NOT EXISTS supply_chain.supplier_metrics (
  partner_id VARCHAR(32),
  partner_name VARCHAR(256),
  total_invoices INTEGER,
  late_invoices INTEGER,
  avg_days_to_pay DOUBLE PRECISION,
  avg_invoice_amount DOUBLE PRECISION,
  late_rate DOUBLE PRECISION,
  risk_score DOUBLE PRECISION
);
-- COPY commands to load from S3 go here.
