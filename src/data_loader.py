from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DataLoadResult:
    df: pd.DataFrame
    source_path: Path


_CANONICAL_RENAMES = {
    "order date": "order_date",
    "ship date": "ship_date",
    "sub-category": "sub_category",
    "sub category": "sub_category",
    "customer segment": "segment",
    "segment": "segment",
    "product name": "product_name",
    "product id": "product_id",
    "order id": "order_id",
    "row id": "row_id",
    "ship mode": "ship_mode",
    "customer id": "customer_id",
    "customer name": "customer_name",
    "postal code": "postal_code",
}


def _normalize_column_name(col: str) -> str:
    c = str(col).strip()
    c_lower = c.lower().replace("_", " ")
    c_lower = " ".join(c_lower.split())
    if c_lower in _CANONICAL_RENAMES:
        return _CANONICAL_RENAMES[c_lower]

    # default: snake_case
    out = (
        c_lower.replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
    )
    out = "_".join([p for p in out.split() if p])
    return out


def _infer_dayfirst(date_series: pd.Series, sample_size: int = 1000) -> bool:
    values = date_series.dropna().astype(str).head(sample_size)
    if values.empty:
        return False

    counts = {"first_gt_12": 0, "second_gt_12": 0, "total": 0}
    for v in values:
        if "/" not in v:
            continue
        parts = v.split("/")
        if len(parts) < 2:
            continue
        try:
            first = int(parts[0])
            second = int(parts[1])
        except ValueError:
            continue
        counts["total"] += 1
        if first > 12:
            counts["first_gt_12"] += 1
        if second > 12:
            counts["second_gt_12"] += 1

    if counts["total"] == 0:
        return False
    # If we see days > 12 in the first field, it's likely day-first.
    return counts["first_gt_12"] > counts["second_gt_12"]


def _parse_datetime(df: pd.DataFrame, col: str) -> pd.Series:
    s = df[col]
    dayfirst = _infer_dayfirst(s)
    parsed = pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)
    return parsed


def load_superstore_data(csv_path: str | Path) -> DataLoadResult:
    """Load and clean the Superstore dataset.

    Expected (typical) fields include order_date, ship_date, region, category,
    sub_category, sales, quantity, discount, profit, segment.

    The loader is resilient: if some fields are missing, the pipeline still runs,
    but some analyses will be skipped.
    """

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path, encoding_errors="ignore")
    df.columns = [_normalize_column_name(c) for c in df.columns]

    # Dates
    if "order_date" in df.columns:
        df["order_date"] = _parse_datetime(df, "order_date")
    if "ship_date" in df.columns:
        df["ship_date"] = _parse_datetime(df, "ship_date")

    # Basic type conversions
    numeric_cols: Iterable[str] = [
        c
        for c in ["sales", "profit", "discount", "quantity"]
        if c in df.columns
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "postal_code" in df.columns:
        # Keep as string to preserve leading zeros
        df["postal_code"] = df["postal_code"].astype(str).str.replace(".0", "", regex=False)

    # Clean missing values
    required = [c for c in ["order_date", "sales"] if c in df.columns]
    if required:
        df = df.dropna(subset=required)

    for c in numeric_cols:
        if c in ("discount",):
            # discount often needs 0 when missing
            df[c] = df[c].fillna(0)
        else:
            df[c] = df[c].fillna(0)

    # Categorical: fill Unknown
    for c in ["region", "category", "sub_category", "segment", "product_name"]:
        if c in df.columns:
            df[c] = df[c].astype(str).replace({"nan": np.nan}).fillna("Unknown")

    # Add helpful derived columns
    if "order_date" in df.columns:
        df["order_day"] = df["order_date"].dt.date
        df["order_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()

    # Shipping time (in days)
    if "order_date" in df.columns and "ship_date" in df.columns:
        ship_delta = df["ship_date"] - df["order_date"]
        df["shipping_time_days"] = ship_delta.dt.total_seconds() / 86400.0
        # Guardrail: negative values can happen due to bad rows
        df.loc[df["shipping_time_days"] < 0, "shipping_time_days"] = np.nan

    return DataLoadResult(df=df, source_path=csv_path)
