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
    st.title("Supply Chain Financial Health & Risk Dashboard")
    st.dataframe(filtered_partners)

    st.subheader("Average DSO by Supplier")
    st.bar_chart(filtered_partners.set_index("supplier")["avg_dso"])

    st.subheader("Invoice Amount Trend")
    df["month"] = df["invoice_date"].dt.to_period("M").dt.to_timestamp()
    st.line_chart(df.groupby("month")["amount"].sum())


