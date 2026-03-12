from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .data_loader import load_superstore_data
from .forecasting import ForecastResult, forecast_next_days, prepare_daily_sales
from .kpi_analysis import KPIResults, compute_kpis
from .insights import generate_business_insights
from .customer_analysis import (
    avg_revenue_per_customer_by_segment,
    customers_by_segment,
    sales_by_segment,
    top_customers_by_sales,
)
from .shipping_analysis import shipping_time_by_region, shipping_time_by_ship_mode
from .sales_analysis import (
    daily_sales_trend,
    monthly_sales_trend,
    sales_by_category,
    sales_by_city,
    sales_by_region,
    sales_by_state,
    sales_by_sub_category,
    top_products_by_revenue,
)


@dataclass(frozen=True)
class PipelineArtifacts:
    data: pd.DataFrame
    kpis: KPIResults
    sales_category: pd.DataFrame
    sales_sub_category: pd.DataFrame
    sales_region: pd.DataFrame
    sales_state: pd.DataFrame
    sales_city: pd.DataFrame
    daily_trend: pd.DataFrame
    monthly_trend: pd.DataFrame
    top_revenue_products: pd.DataFrame
    sales_segment: pd.DataFrame
    customers_segment: pd.DataFrame
    avg_rev_per_customer_segment: pd.DataFrame
    top_customers: pd.DataFrame
    shipping_by_ship_mode: pd.DataFrame
    shipping_by_region: pd.DataFrame
    forecast: ForecastResult
    insights: dict[str, Any]


def run_pipeline(dataset_path: str | Path) -> PipelineArtifacts:
    loaded = load_superstore_data(dataset_path)
    df = loaded.df

    kpis = compute_kpis(df)

    daily = prepare_daily_sales(df)
    forecast = forecast_next_days(daily, horizon_days=7)

    artifacts = PipelineArtifacts(
        data=df,
        kpis=kpis,
        sales_category=sales_by_category(df),
        sales_sub_category=sales_by_sub_category(df),
        sales_region=sales_by_region(df),
        sales_state=sales_by_state(df),
        sales_city=sales_by_city(df),
        daily_trend=daily_sales_trend(df),
        monthly_trend=monthly_sales_trend(df),
        top_revenue_products=top_products_by_revenue(df, n=10),
        sales_segment=sales_by_segment(df),
        customers_segment=customers_by_segment(df),
        avg_rev_per_customer_segment=avg_revenue_per_customer_by_segment(df),
        top_customers=top_customers_by_sales(df, n=10),
        shipping_by_ship_mode=shipping_time_by_ship_mode(df),
        shipping_by_region=shipping_time_by_region(df),
        forecast=forecast,
        insights={},
    )

    bi = generate_business_insights(df, avg_shipping_days=kpis.average_shipping_time_days)
    insights: dict[str, Any] = {
        "title": bi.title,
        "bullets": bi.bullets,
    }
    return PipelineArtifacts(**{**artifacts.__dict__, "insights": insights})
