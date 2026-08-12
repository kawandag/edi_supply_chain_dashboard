from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="SupplyScope | Risk Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


COLORS = {
    "navy": "#101828",
    "blue": "#2563EB",
    "cyan": "#06B6D4",
    "green": "#12B76A",
    "amber": "#F79009",
    "red": "#F04438",
    "muted": "#667085",
    "grid": "#EAECF0",
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #F7F8FA; color: #101828; }
    [data-testid="stSidebar"] { background: #101828; border-right: 0; }
    [data-testid="stSidebar"] * { color: #F2F4F7; }
    [data-testid="stSidebar"] .stMultiSelect span,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * { color: #101828; }
    [data-testid="stSidebar"] hr { border-color: #344054; }
    [data-testid="stHeader"] { background: rgba(247,248,250,.88); }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px; }
    .brand { display:flex; align-items:center; gap:.75rem; margin: .35rem 0 1.6rem; }
    .brand-mark { display:grid; place-items:center; width:40px; height:40px; border-radius:12px;
                  background:linear-gradient(135deg,#2E90FA,#06B6D4); font-size:22px; }
    .brand-name { font-size:20px; font-weight:700; color:white; line-height:1; }
    .brand-sub { color:#98A2B3; font-size:11px; margin-top:5px; letter-spacing:.08em; text-transform:uppercase; }
    .eyebrow { color:#2563EB; font-size:12px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
    .hero-title { color:#101828; font-size:32px; line-height:1.2; font-weight:700; margin:5px 0 6px; }
    .hero-copy { color:#667085; font-size:15px; margin-bottom:20px; }
    .status-pill { display:inline-flex; align-items:center; gap:7px; padding:7px 11px; border:1px solid #D0D5DD;
                   border-radius:999px; background:white; color:#344054; font-size:12px; font-weight:600; float:right; }
    .status-dot { width:7px; height:7px; border-radius:50%; background:#12B76A; box-shadow:0 0 0 4px #D1FADF; }
    div[data-testid="stMetric"] { background:white; border:1px solid #EAECF0; padding:18px 20px;
                                  border-radius:14px; box-shadow:0 1px 2px rgba(16,24,40,.04); }
    div[data-testid="stMetricLabel"] { color:#667085; font-size:13px; font-weight:600; }
    div[data-testid="stMetricValue"] { color:#101828; font-size:27px; font-weight:700; }
    div[data-testid="stMetricDelta"] { font-size:12px; }
    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { background:white; border:1px solid #EAECF0;
        border-radius:14px; padding:8px; box-shadow:0 1px 2px rgba(16,24,40,.04); }
    .section-title { font-size:17px; font-weight:700; color:#101828; margin:24px 0 2px; }
    .section-copy { font-size:13px; color:#667085; margin-bottom:10px; }
    .insight { padding:16px 18px; border:1px solid #B2DDFF; background:#EFF8FF; border-radius:12px;
               color:#175CD3; font-size:13px; margin:8px 0 18px; }
    .sidebar-label { color:#98A2B3!important; font-size:11px; font-weight:700; letter-spacing:.1em;
                     text-transform:uppercase; margin:18px 0 8px; }
    .stDownloadButton button { width:100%; border-radius:9px; background:#2563EB; color:white; border:0; font-weight:600; }
    .stDownloadButton button:hover { background:#175CD3; color:white; border:0; }
    #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    path = Path(__file__).parent / "data" / "invoices.csv"
    data = pd.read_csv(path, parse_dates=["invoice_date", "due_date", "payment_date"])
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0)
    data["dso"] = pd.to_numeric(data["dso"], errors="coerce")
    data["days_late"] = (data["payment_date"] - data["due_date"]).dt.days
    data["payment_status"] = data["days_late"].apply(lambda x: "Late" if x > 0 else "On time")
    data["month"] = data["invoice_date"].dt.to_period("M").dt.to_timestamp()
    return data


def aggregate_suppliers(data: pd.DataFrame) -> pd.DataFrame:
    agg = data.groupby("supplier", as_index=False).agg(
        invoices=("invoice_date", "count"),
        avg_dso=("dso", "mean"),
        total_spend=("amount", "sum"),
        late_invoices=("payment_status", lambda values: (values == "Late").sum()),
        avg_days_late=("days_late", "mean"),
    )
    agg["late_rate"] = agg["late_invoices"] / agg["invoices"]
    dso_component = (agg["avg_dso"] / max(agg["avg_dso"].max(), 1)) * 55
    late_component = agg["late_rate"] * 45
    agg["risk_score"] = (dso_component + late_component).round().clip(0, 100).astype(int)
    agg["risk_tier"] = pd.cut(
        agg["risk_score"], bins=[-1, 39, 64, 100], labels=["Low", "Medium", "High"]
    ).astype(str)
    return agg


def style_figure(fig, height=350):
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=24, b=18),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="DM Sans", color=COLORS["muted"], size=12),
        hoverlabel=dict(bgcolor=COLORS["navy"], font_color="white", bordercolor=COLORS["navy"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return fig


df = load_data()
if df.empty:
    st.error("No invoice data is available. Add records to data/invoices.csv and refresh.")
    st.stop()

suppliers = sorted(df["supplier"].dropna().unique())
date_min, date_max = df["invoice_date"].min().date(), df["invoice_date"].max().date()

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">◈</div><div><div class="brand-name">SupplyScope</div>'
        '<div class="brand-sub">Risk intelligence</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-label">Portfolio filters</div>', unsafe_allow_html=True)
    selected_suppliers = st.multiselect("Suppliers", suppliers, default=suppliers)
    selected_dates = st.date_input(
        "Invoice period", value=(date_min, date_max), min_value=date_min, max_value=date_max
    )
    payment_status = st.selectbox("Payment status", ["All", "Late", "On time"])
    st.markdown("---")
    st.markdown('<div class="sidebar-label">Risk settings</div>', unsafe_allow_html=True)
    risk_tiers = st.multiselect("Risk tier", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    st.caption("Risk combines payment speed (55%) and late-payment frequency (45%).")

start_date, end_date = (selected_dates if len(selected_dates) == 2 else (date_min, date_max))
filtered = df[
    df["supplier"].isin(selected_suppliers)
    & df["invoice_date"].dt.date.between(start_date, end_date)
]
if payment_status != "All":
    filtered = filtered[filtered["payment_status"] == payment_status]

if filtered.empty:
    st.warning("No invoices match these filters. Broaden the selections in the sidebar.")
    st.stop()

partner_agg = aggregate_suppliers(filtered)
partner_agg = partner_agg[partner_agg["risk_tier"].isin(risk_tiers)]
if partner_agg.empty:
    st.warning("No suppliers match the selected risk tiers.")
    st.stop()
filtered = filtered[filtered["supplier"].isin(partner_agg["supplier"])]

late_count = int((filtered["payment_status"] == "Late").sum())
late_rate = late_count / len(filtered)
total_spend = filtered["amount"].sum()
avg_dso = filtered["dso"].mean()
high_risk = int((partner_agg["risk_tier"] == "High").sum())

title_col, status_col = st.columns([4, 1])
with title_col:
    st.markdown('<div class="eyebrow">Executive overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Supply chain financial health</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-copy">Monitoring {len(partner_agg)} suppliers across {len(filtered):,} invoices · '
        f'{start_date:%b %d, %Y} – {end_date:%b %d, %Y}</div>', unsafe_allow_html=True
    )
with status_col:
    st.markdown('<div class="status-pill"><span class="status-dot"></span> Data refreshed</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Portfolio spend", f"${total_spend:,.0f}", f"{len(filtered):,} invoices")
k2.metric("Average DSO", f"{avg_dso:.1f} days", f"{avg_dso - 45:+.1f} vs 45-day target", delta_color="inverse")
k3.metric("Late payment rate", f"{late_rate:.1%}", f"{late_count} late payments", delta_color="inverse")
k4.metric("High-risk suppliers", str(high_risk), f"of {len(partner_agg)} monitored", delta_color="inverse")

if high_risk:
    riskiest = partner_agg.sort_values("risk_score", ascending=False).iloc[0]
    st.markdown(
        f'<div class="insight"><strong>Attention recommended:</strong> {riskiest["supplier"]} has the highest '
        f'risk score ({riskiest["risk_score"]}/100), with {riskiest["avg_dso"]:.0f}-day average DSO and '
        f'{riskiest["late_rate"]:.0%} late payments.</div>', unsafe_allow_html=True
    )

left, right = st.columns([1.65, 1])
with left:
    st.markdown('<div class="section-title">Spend & payment trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Monthly invoiced value with average days sales outstanding</div>', unsafe_allow_html=True)
    monthly = filtered.groupby("month", as_index=False).agg(spend=("amount", "sum"), avg_dso=("dso", "mean"))
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(x=monthly["month"], y=monthly["spend"], name="Spend", marker_color="#B2DDFF", hovertemplate="$%{y:,.0f}<extra>Spend</extra>"))
    fig_trend.add_trace(go.Scatter(x=monthly["month"], y=monthly["avg_dso"], name="Avg DSO", yaxis="y2", mode="lines+markers", line=dict(color=COLORS["blue"], width=3), marker=dict(size=7), hovertemplate="%{y:.1f} days<extra>Avg DSO</extra>"))
    style_figure(fig_trend, 365)
    fig_trend.update_layout(yaxis=dict(title="Invoice value", tickprefix="$", tickformat="~s", gridcolor=COLORS["grid"]), yaxis2=dict(title="DSO (days)", overlaying="y", side="right", showgrid=False))
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

with right:
    st.markdown('<div class="section-title">Risk distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Supplier mix by current composite risk tier</div>', unsafe_allow_html=True)
    tier_counts = partner_agg["risk_tier"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
    fig_donut = go.Figure(go.Pie(labels=tier_counts.index, values=tier_counts.values, hole=.68, sort=False, marker=dict(colors=[COLORS["red"], COLORS["amber"], COLORS["green"]]), textinfo="label+value", hovertemplate="%{label}: %{value} suppliers<extra></extra>"))
    style_figure(fig_donut, 365)
    fig_donut.update_layout(showlegend=False, annotations=[dict(text=f"<b>{len(partner_agg)}</b><br><span style='font-size:11px'>SUPPLIERS</span>", x=.5, y=.5, showarrow=False, font_size=20)])
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

left2, right2 = st.columns([1.25, 1])
with left2:
    st.markdown('<div class="section-title">Supplier risk matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Payment velocity versus portfolio exposure · bubble size reflects invoice count</div>', unsafe_allow_html=True)
    fig_scatter = px.scatter(partner_agg, x="avg_dso", y="total_spend", size="invoices", color="risk_tier", hover_name="supplier", color_discrete_map={"High": COLORS["red"], "Medium": COLORS["amber"], "Low": COLORS["green"]}, category_orders={"risk_tier": ["High", "Medium", "Low"]}, labels={"avg_dso": "Average DSO (days)", "total_spend": "Portfolio spend", "risk_tier": "Risk"}, custom_data=["risk_score", "late_rate"])
    fig_scatter.update_traces(hovertemplate="<b>%{hovertext}</b><br>DSO: %{x:.1f} days<br>Spend: $%{y:,.0f}<br>Risk score: %{customdata[0]}<br>Late rate: %{customdata[1]:.0%}<extra></extra>", marker=dict(opacity=.83, line=dict(width=1, color="white")))
    style_figure(fig_scatter, 390)
    fig_scatter.update_yaxes(tickprefix="$", tickformat="~s")
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

with right2:
    st.markdown('<div class="section-title">Supplier risk ranking</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Composite score from 0 (healthiest) to 100 (highest risk)</div>', unsafe_allow_html=True)
    ranking = partner_agg.sort_values("risk_score").tail(8)
    fig_rank = go.Figure(go.Bar(x=ranking["risk_score"], y=ranking["supplier"], orientation="h", marker_color=[{"High": COLORS["red"], "Medium": COLORS["amber"], "Low": COLORS["green"]}[tier] for tier in ranking["risk_tier"]], text=ranking["risk_score"], textposition="outside", hovertemplate="%{y}: %{x}/100<extra></extra>"))
    style_figure(fig_rank, 390)
    fig_rank.update_layout(showlegend=False)
    fig_rank.update_xaxes(range=[0, 105], title="Risk score")
    st.plotly_chart(fig_rank, use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="section-title">Supplier detail</div>', unsafe_allow_html=True)
st.markdown('<div class="section-copy">Sort, search, and compare the portfolio; export the current filtered view from the sidebar</div>', unsafe_allow_html=True)
display = partner_agg.sort_values("risk_score", ascending=False).rename(columns={"supplier": "Supplier", "invoices": "Invoices", "avg_dso": "Avg DSO", "total_spend": "Spend", "late_invoices": "Late", "late_rate": "Late rate", "risk_score": "Risk score", "risk_tier": "Risk tier"})
display = display[["Supplier", "Risk tier", "Risk score", "Spend", "Invoices", "Avg DSO", "Late", "Late rate"]]
st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Spend": st.column_config.NumberColumn(format="$%.0f"),
        "Avg DSO": st.column_config.NumberColumn(format="%.1f days"),
        "Late rate": st.column_config.ProgressColumn(format="%.0%%", min_value=0, max_value=1),
        "Risk score": st.column_config.ProgressColumn(format="%d", min_value=0, max_value=100),
    },
)

with st.sidebar:
    export = display.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered report", export, "supplier_risk_report.csv", "text/csv")
    st.caption(f"{len(filtered):,} records in current view")
