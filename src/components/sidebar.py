"""Sidebar widget — returns filter values."""
import streamlit as st
import pandas as pd


def render_sidebar(df: pd.DataFrame) -> tuple:
    """Render sidebar controls and return (date_range, region, categories, segment)."""
    with st.sidebar:
        st.markdown("## 🛍️ Retail Dashboard")
        st.markdown("---")

        min_date   = df["order_date"].min().date()
        max_date   = df["order_date"].max().date()
        date_range = st.date_input(
            "Date range", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )

        regions  = ["All"] + sorted(df["region"].unique().tolist())
        region   = st.selectbox("Region", regions)

        cats     = sorted(df["category"].unique().tolist())
        selected = st.multiselect("Category", cats, default=cats)

        segs     = ["All"] + sorted(df["segment"].unique().tolist())
        segment  = st.selectbox("Segment", segs)

        st.markdown("---")
        st.caption("Synthetic Superstore dataset · 2021–2024")

    return date_range, region, selected, segment
