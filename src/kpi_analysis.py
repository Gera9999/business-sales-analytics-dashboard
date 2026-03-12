from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class KPIResults:
    total_revenue: float
    average_order_value: float
    total_orders: int
    unique_customers: int
    average_shipping_time_days: float | None

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        # Make JSON-serializable
        for k, v in list(out.items()):
            if isinstance(v, (np.floating, np.integer)):
                out[k] = v.item()
        return out


def compute_kpis(df: pd.DataFrame) -> KPIResults:
    revenue = float(df["sales"].sum()) if "sales" in df.columns else 0.0

    if "order_id" in df.columns:
        total_orders = int(df["order_id"].nunique())
    else:
        total_orders = int(len(df))

    avg_order_value = float(revenue / total_orders) if total_orders else 0.0

    if "customer_id" in df.columns:
        unique_customers = int(df["customer_id"].nunique())
    else:
        unique_customers = int(0)

    avg_shipping: float | None
    if "shipping_time_days" in df.columns:
        avg_shipping = float(pd.to_numeric(df["shipping_time_days"], errors="coerce").mean())
        if np.isnan(avg_shipping):
            avg_shipping = None
    else:
        avg_shipping = None

    return KPIResults(
        total_revenue=revenue,
        average_order_value=avg_order_value,
        total_orders=total_orders,
        unique_customers=unique_customers,
        average_shipping_time_days=avg_shipping,
    )
