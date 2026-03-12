from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastResult:
    history: pd.DataFrame  # columns: ds, y
    forecast: pd.DataFrame  # columns: ds, yhat, yhat_lower, yhat_upper
    model_name: str


def prepare_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    if "order_date" not in df.columns or "sales" not in df.columns:
        return pd.DataFrame(columns=["ds", "y"])

    daily = (
        df.assign(ds=df["order_date"].dt.floor("D"))
        .groupby("ds", as_index=False)["sales"]
        .sum()
        .rename(columns={"sales": "y"})
        .sort_values("ds")
    )
    return daily


def _forecast_with_prophet(history: pd.DataFrame, horizon_days: int) -> Optional[ForecastResult]:
    try:
        from prophet import Prophet  # type: ignore
    except Exception:
        return None

    # Prophet expects columns ds, y
    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.90,
    )
    m.fit(history)

    future = m.make_future_dataframe(periods=horizon_days, freq="D", include_history=True)
    fcst = m.predict(future)

    out = fcst[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon_days)
    return ForecastResult(history=history, forecast=out, model_name="prophet")


def _forecast_naive(history: pd.DataFrame, horizon_days: int) -> ForecastResult:
    """Lightweight fallback forecast (no extra dependencies).

    Uses the mean of the last 7 days (or fewer if unavailable) as the forecast level.
    """

    hist = history.sort_values("ds").copy()
    last_date = hist["ds"].max()
    future_ds = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D")

    tail = hist["y"].tail(min(7, len(hist)))
    level = float(tail.mean()) if len(tail) else 0.0

    # Uncertainty: std of the last 30 days (if available)
    window = hist["y"].tail(min(30, len(hist)))
    sigma = float(np.std(window)) if len(window) > 1 else 0.0
    z = 1.645  # ~90%

    yhat = np.full(shape=(horizon_days,), fill_value=level, dtype=float)
    forecast = pd.DataFrame(
        {
            "ds": future_ds,
            "yhat": yhat,
            "yhat_lower": yhat - z * sigma,
            "yhat_upper": yhat + z * sigma,
        }
    )

    return ForecastResult(history=history, forecast=forecast, model_name="naive_mean")


def forecast_next_days(daily_sales: pd.DataFrame, horizon_days: int = 7) -> ForecastResult:
    """Forecast next `horizon_days` of daily sales.

    Tries Prophet first (if installed and usable). Otherwise, falls back to a lightweight
    baseline (recent mean) without additional dependencies.
    """

    history = daily_sales[["ds", "y"]].dropna().copy()
    history = history.sort_values("ds")

    if history.empty:
        empty_fcst = pd.DataFrame(columns=["ds", "yhat", "yhat_lower", "yhat_upper"])
        return ForecastResult(history=history, forecast=empty_fcst, model_name="none")

    prophet_result = _forecast_with_prophet(history, horizon_days)
    if prophet_result is not None:
        return prophet_result

    return _forecast_naive(history, horizon_days)
