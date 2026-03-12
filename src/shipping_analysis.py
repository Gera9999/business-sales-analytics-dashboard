from __future__ import annotations

import pandas as pd


def _require(df: pd.DataFrame, cols: list[str]) -> bool:
    return all(c in df.columns for c in cols)


def average_shipping_time(df: pd.DataFrame) -> float | None:
    if "shipping_time_days" not in df.columns:
        return None
    s = pd.to_numeric(df["shipping_time_days"], errors="coerce")
    v = float(s.mean())
    return None if pd.isna(v) else v


def shipping_time_by_ship_mode(df: pd.DataFrame) -> pd.DataFrame:
    if not _require(df, ["ship_mode", "shipping_time_days"]):
        return pd.DataFrame(columns=["ship_mode", "avg_shipping_time_days"])

    out = (
        df.groupby("ship_mode", as_index=False)["shipping_time_days"]
        .mean()
        .rename(columns={"shipping_time_days": "avg_shipping_time_days"})
        .sort_values("avg_shipping_time_days")
    )
    return out


def shipping_time_by_region(df: pd.DataFrame) -> pd.DataFrame:
    if not _require(df, ["region", "shipping_time_days"]):
        return pd.DataFrame(columns=["region", "avg_shipping_time_days"])

    out = (
        df.groupby("region", as_index=False)["shipping_time_days"]
        .mean()
        .rename(columns={"shipping_time_days": "avg_shipping_time_days"})
        .sort_values("avg_shipping_time_days")
    )
    return out
