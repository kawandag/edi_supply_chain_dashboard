import os
import zipfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# === 1. Make project folder structure ===
project_name = "supply_chain_streamlit_project"
os.makedirs(project_name, exist_ok=True)
os.makedirs(f"{project_name}/data", exist_ok=True)

# === 2. Create synthetic dataset ===
np.random.seed(42)
suppliers = [f"Supplier {i}" for i in range(1, 11)]
data = []
start_date = datetime(2024, 1, 1)

for supplier in suppliers:
    num_invoices = np.random.randint(1, 6)  # between 1 and 5 invoices
    for _ in range(num_invoices):
        invoice_date = start_date + timedelta(days=int(np.random.randint(0, 365)))
        due_date = invoice_date + timedelta(days=int(np.random.randint(30, 90)))
        payment_date = due_date + timedelta(days=int(np.random.randint(-10, 20)))
        amount = np.random.randint(1000, 5000)
        dso = (payment_date - invoice_date).days
        data.append([supplier, invoice_date, due_date, payment_date, amount, dso])

df = pd.DataFrame(data, columns=["supplier", "invoice_date", "due_date", "payment_date", "amount", "dso"])
df.to_csv(f"{project_name}/data/invoices.csv", index=False)

# === 3. Create Streamlit app ===
app_code = """import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supply Chain Risk Dashboard", layout="wide")

# Load data
df = pd.read_csv("data/invoices.csv", parse_dates=["invoice_date", "due_date", "payment_date"])

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
"""

with open(f"{project_name}/app.py", "w") as f:
    f.write(app_code)

# === 4. Create requirements.txt ===
requirements = """streamlit
pandas
numpy
"""
with open(f"{project_name}/requirements.txt", "w") as f:
    f.write(requirements)

