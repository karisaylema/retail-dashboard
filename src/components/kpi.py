"""KPI cards — rendered as a single flex-row HTML block."""
import streamlit as st
import pandas as pd

from src.config import KPI_GRADIENTS

_CSS = """
<style>
.kpi-row{display:flex;gap:14px;margin-bottom:8px;}
.kpi-card{
    flex:1;min-width:0;height:118px;border-radius:14px;
    padding:18px 20px 14px;position:relative;overflow:hidden;
    box-shadow:0 8px 28px rgba(0,0,0,.38);
    display:flex;flex-direction:column;justify-content:space-between;
}
.kpi-card::before{
    content:"";position:absolute;top:-28px;right:-28px;
    width:90px;height:90px;border-radius:50%;
    background:rgba(255,255,255,.09);pointer-events:none;
}
.kpi-card::after{
    content:"";position:absolute;bottom:-20px;left:-20px;
    width:60px;height:60px;border-radius:50%;
    background:rgba(255,255,255,.05);pointer-events:none;
}
.kpi-top{display:flex;flex-direction:column;gap:4px;}
.kpi-label{
    font-size:.68rem;font-weight:700;letter-spacing:1.6px;
    text-transform:uppercase;color:rgba(255,255,255,.65);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.kpi-value{
    font-size:1.75rem;font-weight:800;color:#fff;line-height:1;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.kpi-sub{font-size:.73rem;color:rgba(255,255,255,.5);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
</style>
"""


def _card(label: str, value: str, sub: str, gradient: str) -> str:
    return (
        f'<div class="kpi-card" style="background:{gradient};">'
        f'<div class="kpi-top">'
        f'<span class="kpi-label">{label}</span>'
        f'<span class="kpi-value">{value}</span>'
        f'</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )


def render_kpis(df: pd.DataFrame) -> None:
    """Compute KPIs from df and render the card row."""
    total_sales       = df["sales"].sum()
    total_profit      = df["profit"].sum()
    total_orders      = df["order_id"].nunique()
    avg_order_value   = total_sales / total_orders if total_orders else 0
    profit_margin_pct = (total_profit / total_sales * 100) if total_sales else 0
    total_qty         = df["quantity"].sum()

    margin_grad = (KPI_GRADIENTS["margin_pos"] if profit_margin_pct >= 0
                   else KPI_GRADIENTS["margin_neg"])

    cards = (
        _card("Total Sales",     f"${total_sales:,.0f}",      f"🛒 {total_qty:,} units sold",   KPI_GRADIENTS["sales"])
        + _card("Total Profit",  f"${total_profit:,.0f}",     "💰 Net after discounts",          KPI_GRADIENTS["profit"])
        + _card("Total Orders",  f"{total_orders:,}",         "📦 Unique order IDs",             KPI_GRADIENTS["orders"])
        + _card("Avg Order Value", f"${avg_order_value:,.0f}","📊 Revenue per order",            KPI_GRADIENTS["aov"])
        + _card("Profit Margin", f"{profit_margin_pct:.1f}%", "📈 Sales → profit ratio",        margin_grad)
    )

    st.markdown(_CSS + f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
