import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Supply Chain Risk Dashboard", layout="wide")

# Load data

BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "data", "invoices.csv")

df = pd.read_csv(csv_path, parse_dates=["invoice_date", "due_date", "payment_date"])

# Aggregate partner metrics
partner_agg = df.groupby("supplier").agg(
    total_invoices=("invoice_date", "count"),
    avg_dso=("dso", "mean"),
    total_amount=("amount", "sum")
).reset_index()

partner_agg["risk_score"] = (partner_agg["avg_dso"] / 60.0) + partner_agg["total_invoices"] / 10.0

# Sidebar filters
if partner_agg.empty:
    st.error("No data available.")
else:
    min_count = int(partner_agg["total_invoices"].min())
    max_count = int(partner_agg["total_invoices"].max())

    if min_count == max_count:
        st.sidebar.info(f"All suppliers have {min_count} invoices.")
        min_invoices = min_count
    else:
        min_invoices = st.sidebar.slider(
            "Minimum invoices per supplier", 
            min_count, 
            max_count, 
            min_count
        )

    filtered_partners = partner_agg[partner_agg["total_invoices"] >= min_invoices]

    # Layout
    st.title("📊 Supply Chain Financial Assessment Dashboard")
    st.markdown("Gain insights into supplier risk, invoice trends, and payment performance.")

    # KPI Metrics
    total_inv = int(filtered_partners["total_invoices"].sum())
    avg_dso_val = round(filtered_partners["avg_dso"].mean(), 2)
    total_amt = round(filtered_partners["total_amount"].sum(), 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invoices", f"{total_inv:,}")
    col2.metric("Avg DSO (days)", avg_dso_val)
    col3.metric("Total Spend ($)", f"{total_amt:,.0f}")

    # Supplier Risk Table
    st.subheader("🔎 Supplier Risk Overview")
    st.dataframe(filtered_partners.style.format({
        "avg_dso": "{:.1f}", 
        "total_amount": "${:,.0f}", 
        "risk_score": "{:.2f}"
    }))

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Average DSO by Supplier")
        st.bar_chart(filtered_partners.set_index("supplier")["avg_dso"])

    with col2:
        st.subheader("💰 Total Spend by Supplier")
        st.bar_chart(filtered_partners.set_index("supplier")["total_amount"])

    st.subheader("📈 Monthly Invoice Amount Trend")
    df["month"] = df["invoice_date"].dt.to_period("M").dt.to_timestamp()
    st.line_chart(df.groupby("month")["amount"].sum())


