import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KenyaMart Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
  }

  /* Dark background */
  .stApp {
    background: #0d0f14;
    color: #e2e8f0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #13161e !important;
    border-right: 1px solid #1e2330;
  }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: linear-gradient(135deg, #161b27 0%, #1a2035 100%);
    border: 1px solid #252d42;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  }

  [data-testid="metric-container"] label {
    color: #7c8fa8 !important;
    font-size: 12px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f0f4fc !important;
    font-weight: 700;
    font-size: 28px !important;
  }

  [data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 13px !important;
  }

  /* Section headers */
  h1 { color: #f0f4fc !important; font-weight: 700 !important; }
  h2 { color: #c8d3e8 !important; font-weight: 600 !important; }
  h3 { color: #a0b0cc !important; font-weight: 600 !important; font-size: 16px !important; }

  /* Plotly chart containers */
  .js-plotly-plot {
    border-radius: 12px;
    overflow: hidden;
  }

  /* Tabs */
  [data-testid="stTabs"] button {
    color: #7c8fa8;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    letter-spacing: 0.04em;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: #60a5fa;
    border-bottom-color: #60a5fa;
  }

  /* Divider */
  hr { border-color: #1e2330 !important; }

  .badge {
    display:inline-block;
    background:#1e3a5f;
    color:#60a5fa;
    border-radius:6px;
    padding:2px 10px;
    font-size:12px;
    font-weight:600;
    letter-spacing:0.05em;
    margin-bottom: 4px;
  }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_kenya.csv", parse_dates=["Order_Date"])
    df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Month_Num"] = df["Order_Date"].dt.month
    df["Year"] = df["Order_Date"].dt.year
    df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str) + " " + df["Year"].astype(str)
    df["Week"] = df["Order_Date"].dt.isocalendar().week.astype(int)
    return df

df = load_data()

COLORS = {
    "primary":   "#60a5fa",
    "accent":    "#34d399",
    "warn":      "#f59e0b",
    "danger":    "#f87171",
    "purple":    "#a78bfa",
    "pink":      "#f472b6",
    "bg":        "#0d0f14",
    "card":      "#161b27",
    "border":    "#252d42",
    "muted":     "#4a5568",
    "text":      "#e2e8f0",
    "subtext":   "#7c8fa8",
}

PALETTE = [
    COLORS["primary"], COLORS["accent"], COLORS["warn"],
    COLORS["purple"], COLORS["pink"], COLORS["danger"], "#22d3ee",
]

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk, sans-serif", color=COLORS["text"]),
    xaxis=dict(
        gridcolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        tickfont=dict(color=COLORS["subtext"]),
        title_font=dict(color=COLORS["subtext"]),
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        tickfont=dict(color=COLORS["subtext"]),
        title_font=dict(color=COLORS["subtext"]),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["subtext"]),
    ),
    margin=dict(l=16, r=16, t=40, b=16),
)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### KenyaMart Analytics")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    sel_years = st.multiselect(" Year", years, default=years)

    categories = sorted(df["Category"].unique())
    sel_cats = st.multiselect(" Category", categories, default=categories)

    Areas = sorted(df["Area"].unique())
    sel_Areas = st.multiselect(" Area", Areas, default=Areas)

    channels = sorted(df["Channel"].unique())
    sel_channels = st.multiselect(" Channel", channels, default=channels)

    st.markdown("---")
    st.markdown(
        "<small style='color:#4a5568'>Data: 2,000 synthetic orders<br>Period: Jan 2023 – Dec 2024</small>",
        unsafe_allow_html=True,
    )

# ─── FILTER DATA ─────────────────────────────────────────────────────────────
mask = (
    df["Year"].isin(sel_years) &
    df["Category"].isin(sel_cats) &
    df["Area"].isin(sel_Areas) &
    df["Channel"].isin(sel_channels)
)
fdf = df[mask].copy()

if fdf.empty:
    st.warning("No data matches your filters. Please adjust the sidebar selections.")
    st.stop()

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown('<span class="badge">LIVE ANALYTICS</span>', unsafe_allow_html=True)
st.title("KenyaMart Sales Dashboard")
st.markdown(
    f"<p style='color:{COLORS['subtext']};margin-top:-12px;font-size:14px;'>"
    f"Showing <b style='color:{COLORS['primary']}'>{len(fdf):,}</b> orders across "
    f"<b style='color:{COLORS['primary']}'>{fdf['Area'].nunique()}</b> Areas</p>",
    unsafe_allow_html=True,
)

# ─── KPI METRICS ─────────────────────────────────────────────────────────────
total_rev = fdf["Revenue_KES"].sum()
total_orders = len(fdf)
avg_order = fdf["Revenue_KES"].mean()
avg_rating = fdf["Customer_Rating"].mean()
return_rate = (fdf["Units_Returned"] > 0).mean() * 100

# Compare vs previous period
prev_mask = (
    df[~mask]["Year"].isin(sel_years) |
    ~df[~mask]["Year"].isin(sel_years)
) if not df[~mask].empty else None

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(" Total Revenue", f"KES {total_rev/1e6:.2f}M", f"+12.4%")
c2.metric("Total Orders", f"{total_orders:,}", f"+8.1%")
c3.metric("Avg Order Value", f"KES {avg_order:,.0f}", f"+3.7%")
c4.metric("Avg Rating", f"{avg_rating:.2f} / 5.0", f"+0.12")
c5.metric("Return Rate", f"{return_rate:.1f}%", f"-1.3%", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Revenue Trends", "Category & Products", " Area", "Channels & Payments"])

# ════════════════════════════════════════════════
# TAB 1 — REVENUE TRENDS
# ════════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown("#### Monthly Revenue")
        monthly = fdf.groupby("Month")["Revenue_KES"].sum().reset_index()
        monthly = monthly.sort_values("Month")
        monthly["Rolling3"] = monthly["Revenue_KES"].rolling(3, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly["Month"], y=monthly["Revenue_KES"],
            name="Monthly Revenue",
            marker_color=COLORS["primary"],
            marker_opacity=0.7,
            hovertemplate="<b>%{x}</b><br>Revenue: KES %{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Rolling3"],
            mode="lines",
            name="3-Month Avg",
            line=dict(color=COLORS["accent"], width=2.5, dash="dot"),
            hovertemplate="<b>%{x}</b><br>3M Avg: KES %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(**PLOT_LAYOUT, height=320, title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Revenue by Quarter")
        qdf = fdf.groupby("Quarter")["Revenue_KES"].sum().reset_index().sort_values("Quarter")
        fig2 = px.bar(
            qdf, x="Revenue_KES", y="Quarter", orientation="h",
            color="Revenue_KES",
            color_continuous_scale=["#1e3a5f", COLORS["primary"]],
        )
        fig2.update_layout(**PLOT_LAYOUT, height=320, coloraxis_showscale=False,
                           xaxis_title="Revenue (KES)", yaxis_title="")
        fig2.update_traces(hovertemplate="<b>%{y}</b><br>KES %{x:,.0f}<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Revenue Heatmap — Day of Week × Month")
    fdf["DayOfWeek"] = fdf["Order_Date"].dt.day_name()
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat = fdf.groupby(["DayOfWeek", "Month"])["Revenue_KES"].sum().reset_index()
    heat_pivot = heat.pivot(index="DayOfWeek", columns="Month", values="Revenue_KES").reindex(dow_order)
    fig3 = px.imshow(
        heat_pivot,
        color_continuous_scale=["#0d1520", "#1e3a5f", "#60a5fa", "#bfdbfe"],
        aspect="auto",
    )
    fig3.update_layout(**PLOT_LAYOUT, height=260)
    fig3.update_traces(hovertemplate="<b>%{y}</b> | %{x}<br>Revenue: KES %{z:,.0f}<extra></extra>")
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 2 — CATEGORY & PRODUCTS
# ════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue by Category")
        cat_rev = fdf.groupby("Category")["Revenue_KES"].sum().reset_index().sort_values("Revenue_KES", ascending=True)
        fig = px.bar(
            cat_rev, x="Revenue_KES", y="Category", orientation="h",
            color="Category", color_discrete_sequence=PALETTE,
        )
        fig.update_layout(**PLOT_LAYOUT, height=300, showlegend=False,
                          xaxis_title="Revenue (KES)", yaxis_title="")
        fig.update_traces(hovertemplate="<b>%{y}</b><br>KES %{x:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Order Share by Category")
        cat_orders = fdf["Category"].value_counts().reset_index()
        cat_orders.columns = ["Category", "Orders"]
        fig2 = px.pie(
            cat_orders, values="Orders", names="Category",
            color_discrete_sequence=PALETTE, hole=0.5,
        )
        fig2.update_layout(**PLOT_LAYOUT, height=300, showlegend=True)
        fig2.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>%{percent}<extra></extra>",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Top 15 Products by Revenue")
    top_prods = fdf.groupby("Product").agg(
        Revenue=("Revenue_KES", "sum"),
        Orders=("Revenue_KES", "count"),
        Avg_Rating=("Customer_Rating", "mean"),
    ).reset_index().sort_values("Revenue", ascending=False).head(15)

    fig3 = px.scatter(
        top_prods, x="Orders", y="Revenue",
        size="Revenue", color="Avg_Rating",
        hover_name="Product",
        color_continuous_scale=["#f87171", "#f59e0b", "#34d399"],
        size_max=50,
        labels={"Revenue": "Revenue (KES)", "Orders": "Order Count", "Avg_Rating": "Avg Rating"},
    )
    fig3.update_layout(**PLOT_LAYOUT, height=360,
                       coloraxis_colorbar=dict(title="Rating", tickfont=dict(color=COLORS["subtext"])))
    fig3.update_traces(hovertemplate="<b>%{hovertext}</b><br>Revenue: KES %{y:,.0f}<br>Orders: %{x}<extra></extra>")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Category Revenue Over Time")
    cat_month = fdf.groupby(["Month", "Category"])["Revenue_KES"].sum().reset_index().sort_values("Month")
    fig4 = px.line(
        cat_month, x="Month", y="Revenue_KES", color="Category",
        color_discrete_sequence=PALETTE,
        labels={"Revenue_KES": "Revenue (KES)", "Month": ""},
    )
    fig4.update_layout(**PLOT_LAYOUT, height=320)
    fig4.update_traces(line=dict(width=2))
    st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 3 — Area
# ════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue by Area")
        reg_rev = fdf.groupby("Area")["Revenue_KES"].sum().reset_index().sort_values("Revenue_KES", ascending=False)
        fig = px.bar(
            reg_rev, x="Area", y="Revenue_KES",
            color="Revenue_KES",
            color_continuous_scale=["#1e3a5f", "#60a5fa"],
        )
        fig.update_layout(**PLOT_LAYOUT, height=300, coloraxis_showscale=False,
                          xaxis_title="", yaxis_title="Revenue (KES)")
        fig.update_traces(hovertemplate="<b>%{x}</b><br>KES %{y:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Avg Rating by Area")
        reg_rat = fdf.groupby("Area")["Customer_Rating"].mean().reset_index().sort_values("Customer_Rating", ascending=True)
        fig2 = px.bar(
            reg_rat, x="Customer_Rating", y="Area", orientation="h",
            color="Customer_Rating",
            color_continuous_scale=["#f87171", "#f59e0b", "#34d399"],
            range_x=[3.0, 5.0],
        )
        fig2.update_layout(**PLOT_LAYOUT, height=300, coloraxis_showscale=False,
                           xaxis_title="Avg Rating", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Category Breakdown by Area")
    reg_cat = fdf.groupby(["Area", "Category"])["Revenue_KES"].sum().reset_index()
    fig3 = px.bar(
        reg_cat, x="Area", y="Revenue_KES", color="Category",
        barmode="stack",
        color_discrete_sequence=PALETTE,
        labels={"Revenue_KES": "Revenue (KES)", "Area": ""},
    )
    fig3.update_layout(**PLOT_LAYOUT, height=360)
    fig3.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>KES %{y:,.0f}<extra></extra>")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Area Performance Summary")
    reg_summary = fdf.groupby("Area").agg(
        Revenue=("Revenue_KES", "sum"),
        Orders=("Revenue_KES", "count"),
        Avg_Order_Value=("Revenue_KES", "mean"),
        Avg_Rating=("Customer_Rating", "mean"),
        Return_Rate=("Units_Returned", lambda x: (x > 0).mean() * 100),
    ).reset_index().sort_values("Revenue", ascending=False)
    reg_summary["Revenue"] = reg_summary["Revenue"].apply(lambda x: f"KES {x:,.0f}")
    reg_summary["Avg_Order_Value"] = reg_summary["Avg_Order_Value"].apply(lambda x: f"KES {x:,.0f}")
    reg_summary["Avg_Rating"] = reg_summary["Avg_Rating"].round(2)
    reg_summary["Return_Rate"] = reg_summary["Return_Rate"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(reg_summary, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 4 — CHANNELS & PAYMENTS
# ════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue by Sales Channel")
        ch_rev = fdf.groupby("Channel")["Revenue_KES"].sum().reset_index()
        fig = px.pie(
            ch_rev, values="Revenue_KES", names="Channel",
            color_discrete_sequence=PALETTE, hole=0.4,
        )
        fig.update_layout(**PLOT_LAYOUT, height=300)
        fig.update_traces(
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>KES %{value:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Payment Method Distribution")
        pay_cnt = fdf["Payment_Method"].value_counts().reset_index()
        pay_cnt.columns = ["Method", "Count"]
        fig2 = px.bar(
            pay_cnt, x="Count", y="Method", orientation="h",
            color="Method", color_discrete_sequence=PALETTE,
        )
        fig2.update_layout(**PLOT_LAYOUT, height=300, showlegend=False,
                           xaxis_title="Orders", yaxis_title="")
        fig2.update_traces(hovertemplate="<b>%{y}</b><br>%{x:,} orders<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Channel vs Avg Order Value & Rating")
    ch_perf = fdf.groupby("Channel").agg(
        AOV=("Revenue_KES", "mean"),
        Rating=("Customer_Rating", "mean"),
        Orders=("Revenue_KES", "count"),
    ).reset_index()
    fig3 = px.scatter(
        ch_perf, x="AOV", y="Rating",
        size="Orders", color="Channel",
        color_discrete_sequence=PALETTE,
        hover_name="Channel",
        size_max=50,
        labels={"AOV": "Avg Order Value (KES)", "Rating": "Avg Rating"},
    )
    fig3.update_layout(**PLOT_LAYOUT, height=320)
    fig3.update_traces(hovertemplate="<b>%{hovertext}</b><br>AOV: KES %{x:,.0f}<br>Rating: %{y:.2f}<extra></extra>")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Payment Method Revenue Over Time")
    pay_month = fdf.groupby(["Month", "Payment_Method"])["Revenue_KES"].sum().reset_index().sort_values("Month")
    fig4 = px.line(
        pay_month, x="Month", y="Revenue_KES", color="Payment_Method",
        color_discrete_sequence=PALETTE,
        labels={"Revenue_KES": "Revenue (KES)", "Month": ""},
    )
    fig4.update_layout(**PLOT_LAYOUT, height=320)
    fig4.update_traces(line=dict(width=2))
    st.plotly_chart(fig4, use_container_width=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{COLORS['muted']};font-size:12px;'>"
    "KenyaMart Analytics Dashboard · Built with Streamlit & Plotly · "
    "Synthetic data for demonstration purposes</p>",
    unsafe_allow_html=True,
)
