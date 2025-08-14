import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from edi_parser import parse_edi_810, parse_edi_820

st.set_page_config(page_title="Supply Chain Financial Health Dashboard", layout="wide")
st.title("📊 Supply Chain Financial Health & Risk Analytics Dashboard")

# Sidebar controls
st.sidebar.header("Data Controls")
regen = st.sidebar.button("Generate fresh mock EDI")
sample_dir = Path("sample_data")
sample_dir.mkdir(exist_ok=True)

# If requested, regenerate mock EDI
if regen or not (sample_dir / "invoice_810.edi").exists() or not (sample_dir / "payment_820.edi").exists():
    from edi_generator import generate_edi_810, generate_edi_820
    (sample_dir / "invoice_810.edi").write_text(generate_edi_810())
    (sample_dir / "payment_820.edi").write_text(generate_edi_820())

# Parse EDI
inv_path = sample_dir / "invoice_810.edi"
pay_path = sample_dir / "payment_820.edi"
invoices = parse_edi_810(str(inv_path))
payments = parse_edi_820(str(pay_path))

# Merge & compute metrics
df = pd.merge(invoices, payments, on=["invoice_number","payer_id"], how="left")
df["dso_days"] = (pd.to_datetime(df["payment_date"]) - pd.to_datetime(df["invoice_date"])).dt.days
df["is_paid"] = df["payment_date"].notna()
df["is_late"] = (df["dso_days"] > df["terms"]).fillna(True)

# Risk score: simple heuristic combining lateness and DSO
df["dso_days_filled"] = df["dso_days"].fillna(df["terms"])  # unpaid treated as at-terms
partner_agg = df.groupby(["payer_id"], as_index=False).agg(
    total_invoices=("invoice_number","count"),
    late_invoices=("is_late","sum"),
    avg_dso=("dso_days_filled","mean"),
    avg_amount=("amount","mean")
)
partner_agg["late_rate"] = partner_agg["late_invoices"] / partner_agg["total_invoices"]
partner_agg["risk_score"] = (partner_agg["avg_dso"] / 60.0) + partner_agg["late_rate"]

# Filters
max_invoices = int(partner_agg["total_invoices"].max())
if max_invoices > 1:
    min_invoices = st.sidebar.slider("Minimum invoices per supplier", 1, max_invoices)
else:
    st.sidebar.write("Only one invoice per supplier in dataset.")
    min_invoices = 1
min_invoices = st.sidebar.slider("Minimum invoices per supplier", 1, int(partner_agg["total_invoices"].max() or 1), 1)
filtered_partners = partner_agg[partner_agg["total_invoices"] >= min_invoices]

# Layout
col1, col2 = st.columns(2)
fig1 = px.bar(filtered_partners.sort_values("avg_dso", ascending=False), x="payer_id", y="avg_dso",
              title="Average DSO by Supplier")
col1.plotly_chart(fig1, use_container_width=True)

# DSO trend over invoice date
trend = df.groupby("invoice_date", as_index=False)["dso_days_filled"].mean().rename(columns={"dso_days_filled":"avg_dso"})
fig2 = px.line(trend.sort_values("invoice_date"), x="invoice_date", y="avg_dso", title="DSO Trend Over Time")
col2.plotly_chart(fig2, use_container_width=True)

# Detailed table
st.subheader("📋 Invoice-to-Payment Details")
st.dataframe(df[["invoice_number","payer_id","invoice_date","payment_date","terms","amount","dso_days","is_late"]])

# Risk table
st.subheader("⚠️ Supplier Risk Scores")
st.dataframe(filtered_partners.sort_values("risk_score", ascending=False))

st.caption("Demo: Parses mock EDI 810/820, computes DSO & risk. Ready for Streamlit Cloud deployment.")
