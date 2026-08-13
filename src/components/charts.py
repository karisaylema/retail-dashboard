"""All Plotly chart builder functions. Each returns a go.Figure."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.config import COLOR_MAP, PLOT_BG, PAPER_BG, GRID_CLR, TEXT_CLR, TOOLTIP

_LAYOUT = dict(
    plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
    font=dict(color=TEXT_CLR), hoverlabel=dict(**TOOLTIP),
    margin=dict(l=0, r=0, t=10, b=0),
)
_AXIS_X = dict(color=TEXT_CLR, showgrid=False, linecolor="#2d3148")
_AXIS_Y = dict(color=TEXT_CLR, showgrid=True, gridcolor=GRID_CLR)


def monthly_dual_axis(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.groupby("month_dt")
          .agg(sales=("sales","sum"), profit=("profit","sum"),
               orders=("order_id","nunique"))
          .reset_index()
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=monthly["month_dt"], y=monthly["sales"], name="Sales",
            marker_color="#6366f1", opacity=0.85,
            customdata=np.stack([monthly["orders"], monthly["profit"]], axis=-1),
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Sales: <b>$%{y:,.0f}</b><br>"
                "Profit: <b>$%{customdata[1]:,.0f}</b><br>"
                "Orders: <b>%{customdata[0]:,}</b><extra></extra>"
            ),
        ), secondary_y=False)
    fig.add_trace(
        go.Scatter(
            x=monthly["month_dt"], y=monthly["profit"], name="Profit",
            line=dict(color="#fbbf24", width=2.5), mode="lines+markers",
            marker=dict(size=5), customdata=monthly["orders"],
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Profit: <b>$%{y:,.0f}</b><br>"
                "Orders: <b>%{customdata:,}</b><extra></extra>"
            ),
        ), secondary_y=True)
    fig.update_layout(
        height=320, **_LAYOUT,
        legend=dict(orientation="h", y=1.12, font=dict(color=TEXT_CLR)),
        xaxis=_AXIS_X, yaxis=_AXIS_Y,
    )
    fig.update_yaxes(title_text="Sales ($)",  secondary_y=False, color=TEXT_CLR, gridcolor=GRID_CLR)
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True,  color=TEXT_CLR, showgrid=False)
    return fig


def category_donut(df: pd.DataFrame) -> go.Figure:
    cat = (df.groupby("category")
             .agg(sales=("sales","sum"), orders=("order_id","nunique"),
                  profit=("profit","sum"))
             .reset_index())
    fig = px.pie(
        cat, names="category", values="sales",
        color="category", color_discrete_map=COLOR_MAP, hole=0.5,
        custom_data=["orders", "profit"],
    )
    fig.update_traces(
        textposition="outside", textinfo="percent+label",
        textfont=dict(color=TEXT_CLR),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sales: <b>$%{value:,.0f}</b><br>"
            "Share: <b>%{percent}</b><br>"
            "Orders: <b>%{customdata[0]:,}</b><br>"
            "Profit: <b>$%{customdata[1]:,.0f}</b><extra></extra>"
        ),
    )
    fig.update_layout(height=320, showlegend=False,
                      paper_bgcolor=PAPER_BG, hoverlabel=dict(**TOOLTIP),
                      margin=dict(l=0, r=0, t=10, b=0))
    return fig


def region_bars(df: pd.DataFrame) -> go.Figure:
    rdf = (df.groupby("region")
             .agg(sales=("sales","sum"), profit=("profit","sum"),
                  orders=("order_id","nunique"), qty=("quantity","sum"))
             .reset_index().sort_values("sales", ascending=True))
    fig = px.bar(
        rdf, x="sales", y="region", orientation="h",
        color="profit", color_continuous_scale="RdYlGn",
        custom_data=["orders", "qty", "profit"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Sales: <b>$%{x:,.0f}</b><br>"
            "Profit: <b>$%{customdata[2]:,.0f}</b><br>"
            "Orders: <b>%{customdata[0]:,}</b><br>"
            "Units: <b>%{customdata[1]:,}</b><extra></extra>"
        ),
        text=rdf["sales"].apply(lambda v: f"${v/1e3:,.0f}k"),
        textposition="outside", textfont=dict(color=TEXT_CLR),
    )
    fig.update_layout(height=300, coloraxis_showscale=False,
                      xaxis=dict(**_AXIS_Y), yaxis=dict(color=TEXT_CLR),
                      margin=dict(l=0, r=70, t=10, b=0), **{
                          k: v for k, v in _LAYOUT.items() if k != "margin"
                      })
    return fig


def subcategory_bars(df: pd.DataFrame) -> go.Figure:
    sdf = (df.groupby(["sub_category","category"])
             .agg(sales=("sales","sum"), profit=("profit","sum"),
                  orders=("order_id","nunique"))
             .reset_index()
             .sort_values("sales", ascending=False).head(10))
    fig = px.bar(
        sdf, x="sales", y="sub_category", orientation="h",
        color="category", color_discrete_map=COLOR_MAP,
        custom_data=["profit","orders","category"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b> · %{customdata[2]}<br>"
            "Sales: <b>$%{x:,.0f}</b><br>"
            "Profit: <b>$%{customdata[0]:,.0f}</b><br>"
            "Orders: <b>%{customdata[1]:,}</b><extra></extra>"
        ),
    )
    fig.update_layout(height=300, **_LAYOUT,
                      legend=dict(orientation="h", y=-0.18, font=dict(color=TEXT_CLR)),
                      xaxis=_AXIS_Y, yaxis=dict(color=TEXT_CLR))
    return fig


def segment_grouped(df: pd.DataFrame) -> go.Figure:
    sdf = (df.groupby("segment")
             .agg(sales=("sales","sum"), profit=("profit","sum"),
                  orders=("order_id","nunique"))
             .reset_index())
    sdf["margin"] = (sdf["profit"] / sdf["sales"] * 100).round(1)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Sales", x=sdf["segment"], y=sdf["sales"],
        marker_color="#6366f1", marker_line_width=0,
        customdata=np.stack([sdf["orders"], sdf["margin"]], axis=-1),
        hovertemplate=(
            "<b>%{x}</b><br>Sales: <b>$%{y:,.0f}</b><br>"
            "Orders: <b>%{customdata[0]:,}</b><br>"
            "Margin: <b>%{customdata[1]:.1f}%</b><extra></extra>"
        ),
    ))
    fig.add_trace(go.Bar(
        name="Profit", x=sdf["segment"], y=sdf["profit"],
        marker_color="#34d399", marker_line_width=0,
        customdata=sdf["margin"],
        hovertemplate=(
            "<b>%{x}</b><br>Profit: <b>$%{y:,.0f}</b><br>"
            "Margin: <b>%{customdata:.1f}%</b><extra></extra>"
        ),
    ))
    fig.update_layout(
        barmode="group", height=300, **_LAYOUT,
        legend=dict(orientation="h", y=1.12, font=dict(color=TEXT_CLR)),
        xaxis=dict(color=TEXT_CLR, showgrid=False),
        yaxis=_AXIS_Y,
    )
    return fig


def discount_scatter(df: pd.DataFrame) -> go.Figure:
    ddf = df[df["sales"] > 0].copy()
    ddf["discount_pct"] = ddf["discount"] * 100
    sample = ddf.sample(min(800, len(ddf)), random_state=42)
    fig = px.scatter(
        sample, x="discount_pct", y="profit_margin",
        color="category", color_discrete_map=COLOR_MAP,
        custom_data=["product_name","sales","segment"],
        opacity=0.55, trendline="ols",
    )
    fig.update_traces(
        selector=dict(mode="markers"),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Discount: <b>%{x:.0f}%</b><br>"
            "Margin: <b>%{y:.1f}%</b><br>"
            "Sales: <b>$%{customdata[1]:,.0f}</b><br>"
            "Segment: <b>%{customdata[2]}</b><extra></extra>"
        ),
    )
    fig.update_layout(height=300, **_LAYOUT,
                      legend=dict(orientation="h", y=-0.22, font=dict(color=TEXT_CLR)),
                      xaxis=_AXIS_Y, yaxis=_AXIS_Y)
    return fig


def shipping_bars(df: pd.DataFrame) -> go.Figure:
    sdf = (df.groupby("ship_mode")
             .agg(orders=("order_id","nunique"), sales=("sales","sum"),
                  avg_days=("ship_date", lambda x: (
                      df.loc[x.index,"ship_date"] - df.loc[x.index,"order_date"]
                  ).dt.days.mean()))
             .reset_index().sort_values("orders", ascending=False))
    sdf["avg_days"] = sdf["avg_days"].round(1)
    fig = px.bar(
        sdf, x="ship_mode", y="orders",
        color="sales", color_continuous_scale="Blues",
        custom_data=["sales","avg_days"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>Orders: <b>%{y:,}</b><br>"
            "Sales: <b>$%{customdata[0]:,.0f}</b><br>"
            "Avg ship time: <b>%{customdata[1]} days</b><extra></extra>"
        ),
        text=sdf["orders"], textposition="outside",
        textfont=dict(color=TEXT_CLR),
    )
    fig.update_layout(height=300, coloraxis_showscale=False, **_LAYOUT,
                      xaxis=dict(color=TEXT_CLR),
                      yaxis=_AXIS_Y)
    return fig


def top_states(df: pd.DataFrame) -> go.Figure:
    sdf = (df.groupby(["state","region"])
             .agg(sales=("sales","sum"), profit=("profit","sum"),
                  orders=("order_id","nunique"))
             .reset_index()
             .sort_values("sales", ascending=False).head(10))
    sdf["margin"] = (sdf["profit"] / sdf["sales"] * 100).round(1)
    fig = px.bar(
        sdf, x="state", y="sales",
        color="sales", color_continuous_scale="Purples",
        custom_data=["region","orders","profit","margin"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b> · %{customdata[0]}<br>"
            "Sales: <b>$%{y:,.0f}</b><br>"
            "Profit: <b>$%{customdata[2]:,.0f}</b><br>"
            "Margin: <b>%{customdata[3]:.1f}%</b><br>"
            "Orders: <b>%{customdata[1]:,}</b><extra></extra>"
        ),
    )
    fig.update_layout(height=300, coloraxis_showscale=False, **_LAYOUT,
                      xaxis=dict(color=TEXT_CLR, tickangle=-35),
                      yaxis=_AXIS_Y)
    return fig
