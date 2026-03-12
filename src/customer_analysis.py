from __future__ import annotations

import pandas as pd


def _require(df: pd.DataFrame, cols: list[str]) -> bool:
    return all(c in df.columns for c in cols)


def sales_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    if not _require(df, ["segment", "sales"]):
        return pd.DataFrame(columns=["segment", "sales"])
    return (
        df.groupby("segment", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )


def customers_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    if not _require(df, ["segment", "customer_id"]):
        return pd.DataFrame(columns=["segment", "customers"])
    out = (
        df.groupby("segment", as_index=False)["customer_id"]
        .nunique()
        .rename(columns={"customer_id": "customers"})
        .sort_values("customers", ascending=False)
    )
    return out


def avg_revenue_per_customer_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    if not _require(df, ["segment", "customer_id", "sales"]):
        return pd.DataFrame(columns=["segment", "avg_revenue_per_customer"])

    seg_sales = df.groupby("segment", as_index=False)["sales"].sum()
    seg_customers = customers_by_segment(df)
    merged = seg_sales.merge(seg_customers, on="segment", how="left")
    merged["avg_revenue_per_customer"] = merged["sales"] / merged["customers"].replace({0: pd.NA})
    return merged[["segment", "avg_revenue_per_customer"]].sort_values(
        "avg_revenue_per_customer", ascending=False
    )


def top_customers_by_sales(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if not _require(df, ["customer_name", "customer_id", "sales"]):
        return pd.DataFrame(columns=["customer_name", "sales"])

    # Prefer customer_name, but keep id for uniqueness if needed
    tmp = df.copy()
    tmp["customer_label"] = tmp["customer_name"].astype(str)

    out = (
        tmp.groupby("customer_label", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
        .head(n)
        .rename(columns={"customer_label": "customer"})
    )
    return out
