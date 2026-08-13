"""Data loading layer — local CSV or S3, with Streamlit caching."""
import os
import pandas as pd
import numpy as np
import streamlit as st

from src.config import AWS_REGION, S3_BUCKET, S3_KEY, LOCAL_PATH


@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    """Return the retail DataFrame. Reads local file when available, S3 otherwise."""
    if os.path.exists(LOCAL_PATH):
        df = pd.read_csv(LOCAL_PATH, parse_dates=["order_date", "ship_date"])
    else:
        import boto3
        from io import StringIO
        s3  = boto3.client("s3", region_name=AWS_REGION)
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        df  = pd.read_csv(
            StringIO(obj["Body"].read().decode("utf-8")),
            parse_dates=["order_date", "ship_date"],
        )

    df["year"]          = df["order_date"].dt.year
    df["month"]         = df["order_date"].dt.to_period("M").astype(str)
    df["month_dt"]      = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["profit_margin"] = (df["profit"] / df["sales"].replace(0, np.nan)) * 100
    return df


def apply_filters(df: pd.DataFrame, date_range, region: str,
                  categories: list, segment: str) -> pd.DataFrame:
    """Apply sidebar filters and return filtered DataFrame."""
    if len(date_range) == 2:
        df = df[(df["order_date"].dt.date >= date_range[0]) &
                (df["order_date"].dt.date <= date_range[1])]
    if region    != "All": df = df[df["region"]  == region]
    if categories:         df = df[df["category"].isin(categories)]
    if segment   != "All": df = df[df["segment"] == segment]
    return df
