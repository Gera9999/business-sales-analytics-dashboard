from __future__ import annotations

import pandas as pd


def _require_columns(df: pd.DataFrame, cols: list[str]) -> bool:
    return all(c in df.columns for c in cols)


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["category", "sales"]):
        return pd.DataFrame(columns=["category", "sales"])
    return (
        df.groupby("category", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )


def sales_by_sub_category(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["sub_category", "sales"]):
        return pd.DataFrame(columns=["sub_category", "sales"])
    return (
        df.groupby("sub_category", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["region", "sales"]):
        return pd.DataFrame(columns=["region", "sales"])
    return (
        df.groupby("region", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )


def sales_by_state(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["state", "sales"]):
        return pd.DataFrame(columns=["state", "sales"])
    return (
        df.groupby("state", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )


def sales_by_city(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["city", "sales"]):
        return pd.DataFrame(columns=["city", "sales"])
    return (
        df.groupby("city", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )


def daily_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["order_date", "sales"]):
        return pd.DataFrame(columns=["order_day", "sales"])
    tmp = df.assign(order_day=df["order_date"].dt.floor("D"))
    out = tmp.groupby("order_day", as_index=False)["sales"].sum()
    return out.sort_values("order_day")


def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["order_month", "sales"]):
        return pd.DataFrame(columns=["order_month", "sales"])
    out = df.groupby("order_month", as_index=False)["sales"].sum()
    return out.sort_values("order_month")


def profit_by_category(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["category", "profit"]):
        return pd.DataFrame(columns=["category", "profit"])
    return (
        df.groupby("category", as_index=False)["profit"]
        .sum()
        .sort_values("profit", ascending=False)
    )


def top_products_by_revenue(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if not _require_columns(df, ["product_name", "sales"]):
        return pd.DataFrame(columns=["product_name", "sales"])
    return (
        df.groupby("product_name", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
        .head(n)
    )


def top_products_by_profit(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if not _require_columns(df, ["product_name", "profit"]):
        return pd.DataFrame(columns=["product_name", "profit"])
    return (
        df.groupby("product_name", as_index=False)["profit"]
        .sum()
        .sort_values("profit", ascending=False)
        .head(n)
    )


def discount_level_buckets(df: pd.DataFrame) -> pd.Series:
    # Typical discount in Superstore is 0.0–0.8
    bins = [-0.001, 0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 1.0]
    labels = [
        "0%",
        "(0-10%]",
        "(10-20%]",
        "(20-30%]",
        "(30-40%]",
        "(40-60%]",
        ">(60%]",
    ]
    return pd.cut(df["discount"], bins=bins, labels=labels)


def average_profit_by_discount_level(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["discount", "profit"]):
        return pd.DataFrame(columns=["discount_level", "avg_profit"])

    tmp = df[["discount", "profit"]].copy()
    tmp["discount_level"] = discount_level_buckets(tmp)

    out = (
        tmp.groupby("discount_level", as_index=False)["profit"]
        .mean()
        .rename(columns={"profit": "avg_profit"})
    )
    out["discount_level"] = out["discount_level"].astype(str)
    return out


def discount_scatter_data(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_columns(df, ["discount", "profit", "sales"]):
        return pd.DataFrame(columns=["discount", "profit", "sales"])

    return df[["discount", "profit", "sales"]].dropna()
