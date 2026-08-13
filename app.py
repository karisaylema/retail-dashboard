"""Entry point — thin orchestrator that wires components together."""
import streamlit as st

from src.config import PAGE_BG, SIDEBAR_BG
from src.data.loader import load_data, apply_filters
from src.components.sidebar import render_sidebar
from src.components.kpi import render_kpis
from src.components.echarts import render_echarts_area
from src.components import charts

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{ background:{PAGE_BG}; }}
    [data-testid="stSidebar"]          {{ background:{SIDEBAR_BG}; }}
    [data-testid="stSidebar"] *        {{ color:#e2e8f0 !important; }}
    [data-testid="stMetric"]           {{ display:none !important; }}
    .section-title{{
        font-size:.82rem;font-weight:700;letter-spacing:1.2px;
        text-transform:uppercase;color:#94a3b8;margin:12px 0 4px;
    }}
    hr {{ border-color:#2d3148 !important; }}
    .js-plotly-plot .plotly .bg {{ fill:transparent !important; }}
</style>
""", unsafe_allow_html=True)


# ── Data & filters ────────────────────────────────────────────────────────────
df_raw                              = load_data()
date_range, region, cats, segment   = render_sidebar(df_raw)
df                                  = apply_filters(df_raw, date_range, region, cats, segment)

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#e2e8f0;margin-bottom:2px;'>🛍️ Retail Sales Dashboard</h2>",
            unsafe_allow_html=True)
st.markdown(f"<p style='color:#64748b;font-size:.85rem;margin-top:0'>"
            f"{len(df):,} transactions · {df['order_id'].nunique():,} orders</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ── KPI cards ────────────────────────────────────────────────────────────────
render_kpis(df)
st.markdown("<br>", unsafe_allow_html=True)

# ── ECharts animated area ─────────────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Monthly Sales by Category — animated stacked area</p>',
            unsafe_allow_html=True)
render_echarts_area(df)
st.markdown("---")

# ── Row 1: Monthly dual-axis + Category donut ─────────────────────────────────
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<p class="section-title">📈 Monthly Sales & Profit</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.monthly_dual_axis(df), use_container_width=True)
with col2:
    st.markdown('<p class="section-title">🗂️ Sales by Category</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.category_donut(df), use_container_width=True)

# ── Row 2: Region + Sub-categories ───────────────────────────────────────────
col3, col4 = st.columns(2)
with col3:
    st.markdown('<p class="section-title">🗺️ Sales by Region</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.region_bars(df), use_container_width=True)
with col4:
    st.markdown('<p class="section-title">📦 Top Sub-Categories</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.subcategory_bars(df), use_container_width=True)

# ── Row 3: Segment + Discount scatter ────────────────────────────────────────
col5, col6 = st.columns(2)
with col5:
    st.markdown('<p class="section-title">👥 Sales & Profit by Segment</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.segment_grouped(df), use_container_width=True)
with col6:
    st.markdown('<p class="section-title">💸 Discount vs Profit Margin</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.discount_scatter(df), use_container_width=True)

# ── Row 4: Shipping + Top states ─────────────────────────────────────────────
col7, col8 = st.columns(2)
with col7:
    st.markdown('<p class="section-title">🚚 Orders by Shipping Mode</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.shipping_bars(df), use_container_width=True)
with col8:
    st.markdown('<p class="section-title">🏆 Top 10 States by Sales</p>', unsafe_allow_html=True)
    st.plotly_chart(charts.top_states(df), use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🔍 View Raw Data"):
    cols = ["order_date","order_id","customer_name","segment","region","state",
            "category","sub_category","product_name","sales","quantity","discount",
            "profit","ship_mode"]
    st.dataframe(
        df[cols].sort_values("order_date", ascending=False).reset_index(drop=True)
          .style.format({"sales":"${:,.2f}","profit":"${:,.2f}","discount":"{:.0%}"}),
        height=350, use_container_width=True,
    )
    st.download_button(
        "⬇️ Download filtered CSV",
        df[cols].to_csv(index=False).encode("utf-8"),
        "retail_filtered.csv", "text/csv",
    )
