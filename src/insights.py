from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


def format_currency_short(value: float | int | None) -> str:
    """Format currency into a short, executive-friendly string.

    Examples:
    - 1_500_000 -> $1.5M
    - 250_000 -> $250K
    - 12_500 -> $12,500

    Notes:
    - Uses K for >= 100K, M for >= 1M.
    - Keeps commas for smaller values.
    """

    if value is None:
        return "N/A"

    try:
        v = float(value)
    except Exception:
        return "N/A"

    sign = "-" if v < 0 else ""
    a = abs(v)

    if a >= 1_000_000:
        scaled = a / 1_000_000
        decimals = 1 if scaled < 10 else 0
        return f"{sign}${scaled:.{decimals}f}M"
    if a >= 100_000:
        scaled = a / 1_000
        decimals = 0 if scaled >= 100 else 1
        return f"{sign}${scaled:.{decimals}f}K"

    return f"{sign}${a:,.0f}"


@dataclass(frozen=True)
class BusinessInsights:
    title: str
    bullets: list[str]


def generate_business_insights(df: pd.DataFrame, *, avg_shipping_days: float | None) -> BusinessInsights:
    bullets: list[str] = []

    if {"category", "sales"}.issubset(df.columns) and not df.empty:
        best_cat = df.groupby("category")["sales"].sum().sort_values(ascending=False).head(1)
        if not best_cat.empty:
            bullets.append(f"{best_cat.index[0]} is the highest revenue category.")

    if {"segment", "sales"}.issubset(df.columns) and not df.empty:
        best_seg = df.groupby("segment")["sales"].sum().sort_values(ascending=False).head(1)
        if not best_seg.empty:
            bullets.append(f"{best_seg.index[0]} is the largest customer segment by revenue.")

    if {"region", "sales"}.issubset(df.columns) and not df.empty:
        best_region = df.groupby("region")["sales"].sum().sort_values(ascending=False).head(1)
        if not best_region.empty:
            bullets.append(f"{best_region.index[0]} is the top region by revenue.")

    if {"state", "sales"}.issubset(df.columns) and not df.empty:
        best_state = df.groupby("state")["sales"].sum().sort_values(ascending=False).head(1)
        if not best_state.empty:
            bullets.append(f"{best_state.index[0]} is the top performing state by revenue.")

    if {"product_name", "sales"}.issubset(df.columns) and not df.empty:
        best_product = df.groupby("product_name")["sales"].sum().sort_values(ascending=False).head(1)
        if not best_product.empty:
            bullets.append(f"Top selling product: {best_product.index[0]}.")

    if avg_shipping_days is not None and pd.notna(avg_shipping_days):
        bullets.append(f"Average shipping time is approximately {avg_shipping_days:.1f} days.")

    if not bullets:
        bullets = ["Not enough data to generate insights."]

    return BusinessInsights(title="Key Business Insights", bullets=bullets)
