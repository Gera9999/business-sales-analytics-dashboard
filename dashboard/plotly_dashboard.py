from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.pipeline import PipelineArtifacts
from src.insights import format_currency_short


def _fmt_currency(value: float | None) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    return f"${value:,.0f}"


def _fmt_currency_short(value: float | None) -> str:
    return format_currency_short(value)


def _indicator(
    title: str,
    value: float | None,
    *,
    prefix: str = "",
    suffix: str = "",
    valueformat: str = ",.0f",
) -> go.Indicator:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        display_value = None
    else:
        display_value = value

    return go.Indicator(
        mode="number",
        title={"text": title},
        value=display_value,
        number={"prefix": prefix, "suffix": suffix, "valueformat": valueformat},
    )


def _kpi_card(title: str, value_text: str) -> go.Scatter:
    return go.Scatter(
        x=[0.5],
        y=[0.5],
        mode="text",
        text=[f"<b>{value_text}</b><br><span style='font-size:12px'>{title}</span>"],
        textposition="middle center",
        hoverinfo="skip",
        showlegend=False,
    )


def build_sales_dashboard(artifacts: PipelineArtifacts) -> go.Figure:
    template = "plotly_white"
    palette = px.colors.qualitative.Set2

    k = artifacts.kpis

    fig = make_subplots(
        rows=8,
        cols=4,
        specs=[
            [{"type": "xy"}] * 4,
            [{"type": "xy"}, {"type": "xy", "colspan": 3}, None, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "table", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "table", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
        ],
        subplot_titles=(
            "",
            "",
            "",
            "",
            "",
            "Daily Sales Trend",
            "Monthly Sales Trend",
            "7-Day Sales Forecast",
            "Sales by Category",
            "Sales by Sub-Category (Top 15)",
            "Top 10 Products by Revenue",
            "Sales by Segment",
            "Top 10 Customers by Revenue",
            "Sales by Region",
            "Top 10 States by Revenue",
            "Top 10 Cities by Revenue",
            "Shipping Time by Ship Mode",
            "Shipping Time by Region",
        ),
        vertical_spacing=0.07,
        horizontal_spacing=0.06,
    )

    # SECTION 1 – KEY METRICS (KPI cards)
    fig.add_trace(
        _kpi_card("Total Revenue", _fmt_currency_short(k.total_revenue)),
        row=1,
        col=1,
    )
    fig.add_trace(
        _kpi_card("Total Orders", f"{k.total_orders:,}"),
        row=1,
        col=2,
    )
    fig.add_trace(
        _kpi_card("Unique Customers", f"{k.unique_customers:,}"),
        row=1,
        col=3,
    )
    fig.add_trace(
        _kpi_card("Average Order Value (AOV)", _fmt_currency_short(k.average_order_value)),
        row=1,
        col=4,
    )

    # Hide KPI axes
    for c in range(1, 5):
        fig.update_xaxes(visible=False, range=[0, 1], row=1, col=c)
        fig.update_yaxes(visible=False, range=[0, 1], row=1, col=c)

    avg_ship_text = (
        f"{k.average_shipping_time_days:.1f} days"
        if k.average_shipping_time_days is not None and not np.isnan(k.average_shipping_time_days)
        else "N/A"
    )
    fig.add_trace(
        _kpi_card("Avg Shipping Time", avg_ship_text),
        row=2,
        col=1,
    )
    fig.update_xaxes(visible=False, range=[0, 1], row=2, col=1)
    fig.update_yaxes(visible=False, range=[0, 1], row=2, col=1)

    # SECTION 2 – SALES PERFORMANCE (diaria, mensual, forecast)
    daily = artifacts.daily_trend
    if not daily.empty:
        fig.add_trace(
            go.Scatter(
                x=daily["order_day"],
                y=daily["sales"],
                mode="lines",
                name="Daily Sales",
                line={"color": palette[0], "shape": "spline", "smoothing": 0.6, "width": 2},
                hovertemplate="%{x|%b %d, %Y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in daily["sales"].tolist()],
            ),
            row=2,
            col=2,
        )
    else:
        fig.add_annotation(
            text="Not available: missing Order Date and/or Sales.",
            xref="x2 domain",
            yref="y2 domain",
            x=0.5,
            y=0.5,
            showarrow=False,
            row=2,
            col=2,
        )

    trend = artifacts.monthly_trend
    if not trend.empty:
        fig.add_trace(
            go.Scatter(
                x=trend["order_month"],
                y=trend["sales"],
                mode="lines+markers",
                name="Monthly Sales",
                line={"color": palette[1], "shape": "spline", "smoothing": 0.6, "width": 2},
                marker={"size": 6},
                hovertemplate="%{x|%b %Y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in trend["sales"].tolist()],
            ),
            row=3,
            col=1,
        )

    fr = artifacts.forecast
    if fr.model_name != "none" and not fr.history.empty and not fr.forecast.empty:
        fig.add_trace(
            go.Scatter(
                x=fr.history["ds"],
                y=fr.history["y"],
                mode="lines",
                name="History",
                line={"color": palette[0], "shape": "spline", "smoothing": 0.6, "width": 2},
                hovertemplate="%{x|%b %d, %Y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in fr.history["y"].tolist()],
            ),
            row=3,
            col=3,
        )
        fig.add_trace(
            go.Scatter(
                x=fr.forecast["ds"],
                y=fr.forecast["yhat"],
                mode="lines+markers",
                name=f"Forecast ({fr.model_name})",
                line={"color": palette[2], "shape": "spline", "smoothing": 0.6, "width": 2},
                marker={"size": 6},
                hovertemplate="%{x|%b %d, %Y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in fr.forecast["yhat"].tolist()],
            ),
            row=3,
            col=3,
        )
        if {"yhat_lower", "yhat_upper"}.issubset(fr.forecast.columns):
            fig.add_trace(
                go.Scatter(
                    x=pd.concat([fr.forecast["ds"], fr.forecast["ds"][::-1]]),
                    y=pd.concat(
                        [fr.forecast["yhat_upper"], fr.forecast["yhat_lower"][::-1]]
                    ),
                    fill="toself",
                    fillcolor="rgba(100, 149, 237, 0.18)",
                    line={"color": "rgba(0,0,0,0)"},
                    hoverinfo="skip",
                    name="Uncertainty Band",
                    showlegend=False,
                ),
                row=3,
                col=3,
            )

    # SECTION 3 – PRODUCT ANALYSIS
    cat = artifacts.sales_category
    if not cat.empty:
        cat = cat.sort_values("sales", ascending=False)
        fig.add_trace(
            go.Bar(
                x=cat["category"],
                y=cat["sales"],
                name="Sales by Category",
                marker_color=palette[3],
                text=[_fmt_currency_short(v) for v in cat["sales"].tolist()],
                textposition="outside",
                hovertemplate="%{x}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in cat["sales"].tolist()],
            ),
            row=4,
            col=1,
        )
        fig.update_xaxes(
            categoryorder="array",
            categoryarray=cat["category"].tolist(),
            title_text="Category",
            row=4,
            col=1,
        )
        fig.update_yaxes(title_text="Revenue", row=4, col=1)

    subcat = artifacts.sales_sub_category
    if not subcat.empty:
        subcat = subcat.sort_values("sales", ascending=False)
        top_sub = subcat.head(15)
        fig.add_trace(
            go.Bar(
                x=top_sub["sales"],
                y=top_sub["sub_category"],
                orientation="h",
                name="Sales by Sub-Category",
                marker_color=palette[4],
                text=[_fmt_currency_short(v) for v in top_sub["sales"].tolist()],
                textposition="outside",
                hovertemplate="%{y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in top_sub["sales"].tolist()],
            ),
            row=4,
            col=3,
        )
        fig.update_yaxes(autorange="reversed", title_text="Sub-Category", row=4, col=3)
        fig.update_xaxes(title_text="Revenue", row=4, col=3)

    top_prod = artifacts.top_revenue_products
    if not top_prod.empty:
        top_prod = top_prod.sort_values("sales", ascending=False).head(10)
        fig.add_trace(
            go.Table(
                header={"values": ["Product", "Revenue"], "align": "left"},
                cells={
                    "values": [
                        top_prod["product_name"].tolist(),
                        [_fmt_currency_short(v) for v in top_prod["sales"].tolist()],
                    ],
                    "align": "left",
                },
            ),
            row=5,
            col=1,
        )

    # SECTION 4 – CUSTOMER ANALYSIS
    seg = artifacts.sales_segment
    if not seg.empty:
        seg = seg.sort_values("sales", ascending=False)
        fig.add_trace(
            go.Bar(
                x=seg["segment"],
                y=seg["sales"],
                name="Sales by Segment",
                marker_color=palette[5] if len(palette) > 5 else palette[0],
                hovertemplate="%{x}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in seg["sales"].tolist()],
            ),
            row=5,
            col=3,
        )
        fig.update_xaxes(
            categoryorder="array",
            categoryarray=seg["segment"].tolist(),
            title_text="Segment",
            row=5,
            col=3,
        )
        fig.update_yaxes(title_text="Revenue", row=5, col=3)

    top_cust = artifacts.top_customers
    if not top_cust.empty:
        top_cust = top_cust.sort_values("sales", ascending=False).head(10)
        fig.add_trace(
            go.Table(
                header={"values": ["Customer", "Revenue"], "align": "left"},
                cells={
                    "values": [
                        top_cust["customer"].tolist(),
                        [_fmt_currency_short(v) for v in top_cust["sales"].tolist()],
                    ],
                    "align": "left",
                },
            ),
            row=6,
            col=1,
        )

    # SECTION 5 – GEOGRAPHIC ANALYSIS
    reg = artifacts.sales_region
    if not reg.empty:
        reg = reg.sort_values("sales", ascending=False)
        fig.add_trace(
            go.Bar(
                x=reg["region"],
                y=reg["sales"],
                name="Sales by Region",
                marker_color=palette[2],
                hovertemplate="%{x}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in reg["sales"].tolist()],
            ),
            row=6,
            col=3,
        )
        fig.update_xaxes(
            categoryorder="array",
            categoryarray=reg["region"].tolist(),
            title_text="Region",
            row=6,
            col=3,
        )
        fig.update_yaxes(title_text="Revenue", row=6, col=3)

    states = artifacts.sales_state
    if not states.empty:
        states = states.sort_values("sales", ascending=False)
        top_states = states.head(10)
        fig.add_trace(
            go.Bar(
                x=top_states["sales"],
                y=top_states["state"],
                orientation="h",
                name="Top States",
                marker_color=palette[1],
                text=[_fmt_currency_short(v) for v in top_states["sales"].tolist()],
                textposition="outside",
                hovertemplate="%{y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in top_states["sales"].tolist()],
            ),
            row=7,
            col=1,
        )
        fig.update_yaxes(autorange="reversed", title_text="State", row=7, col=1)
        fig.update_xaxes(title_text="Revenue", row=7, col=1)

    cities = artifacts.sales_city
    if not cities.empty:
        cities = cities.sort_values("sales", ascending=False)
        top_cities = cities.head(10)
        fig.add_trace(
            go.Bar(
                x=top_cities["sales"],
                y=top_cities["city"],
                orientation="h",
                name="Top Cities",
                marker_color=palette[0],
                text=[_fmt_currency_short(v) for v in top_cities["sales"].tolist()],
                textposition="outside",
                hovertemplate="%{y}<br><b>%{customdata}</b><extra></extra>",
                customdata=[_fmt_currency_short(v) for v in top_cities["sales"].tolist()],
            ),
            row=7,
            col=3,
        )
        fig.update_yaxes(autorange="reversed", title_text="City", row=7, col=3)
        fig.update_xaxes(title_text="Revenue", row=7, col=3)

    # SECTION 6 – SHIPPING ANALYSIS
    ship_mode = artifacts.shipping_by_ship_mode
    if not ship_mode.empty:
        fig.add_trace(
            go.Bar(
                x=ship_mode["ship_mode"],
                y=ship_mode["avg_shipping_time_days"],
                name="Shipping Time by Ship Mode",
                marker_color=palette[4],
                hovertemplate="%{x}<br><b>%{y:.1f} days</b><extra></extra>",
            ),
            row=8,
            col=1,
        )
        fig.update_yaxes(title_text="Shipping Time (Days)", row=8, col=1)

    ship_region = artifacts.shipping_by_region
    if not ship_region.empty:
        ship_region = ship_region.sort_values("avg_shipping_time_days", ascending=False)
        fig.add_trace(
            go.Bar(
                x=ship_region["avg_shipping_time_days"],
                y=ship_region["region"],
                orientation="h",
                name="Shipping Time by Region",
                marker_color=palette[3],
                hovertemplate="%{y}<br><b>%{x:.1f} days</b><extra></extra>",
            ),
            row=8,
            col=3,
        )
        fig.update_yaxes(autorange="reversed", title_text="Region", row=8, col=3)
        fig.update_xaxes(title_text="Shipping Time (Days)", row=8, col=3)

    # Insights panel (as annotation)
    title = artifacts.insights.get("title", "Key Business Insights")
    bullets = artifacts.insights.get("bullets", [])
    if bullets:
        html = "<br>".join([f"• {b}" for b in bullets])
    else:
        html = "No insights available."

    fig.add_annotation(
        text=f"<b>{title}</b><br>{html}",
        xref="paper",
        yref="paper",
        x=0.0,
        y=-0.08,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        align="left",
        bordercolor="rgba(0,0,0,0.1)",
        borderwidth=1,
        bgcolor="rgba(255,255,255,0.9)",
        font={"size": 12},
    )

    fig.update_layout(
        title={
            "text": "Retail Sales Analytics Dashboard (Global Superstore)",
            "x": 0.01,
            "xanchor": "left",
        },
        height=2100,
        template=template,
        margin={"l": 40, "r": 40, "t": 110, "b": 140},
        showlegend=False,
        font={"size": 12},
        hovermode="x unified",
    )

    # Format
    # Axis formatting for revenue charts
    fig.update_yaxes(tickformat="~s", tickprefix="$", row=2, col=2)
    fig.update_yaxes(tickformat="~s", tickprefix="$", row=3, col=1)
    fig.update_yaxes(tickformat="~s", tickprefix="$", row=3, col=3)
    fig.update_yaxes(tickformat="~s", tickprefix="$", row=4, col=1)
    fig.update_xaxes(tickformat="~s", tickprefix="$", row=4, col=3)
    fig.update_yaxes(tickformat="~s", tickprefix="$", row=5, col=3)
    fig.update_yaxes(tickformat="~s", tickprefix="$", row=6, col=3)
    fig.update_xaxes(tickformat="~s", tickprefix="$", row=7, col=1)
    fig.update_xaxes(tickformat="~s", tickprefix="$", row=7, col=3)

    # Date formatting
    fig.update_xaxes(tickformat="%b %d", row=2, col=2)
    fig.update_xaxes(tickformat="%b %Y", row=3, col=1)
    fig.update_xaxes(tickformat="%b %d", row=3, col=3)
    return fig


def save_dashboard_html(artifacts: PipelineArtifacts, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = build_sales_dashboard(artifacts)
    fig.write_html(str(output_path), include_plotlyjs="cdn", full_html=True)
    return output_path
