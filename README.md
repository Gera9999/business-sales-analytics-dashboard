# Business Sales Analytics Dashboard (Global Superstore)

Portfolio-ready Python project that turns a retail orders dataset into a business-focused analytics pipeline and an interactive BI-style dashboard.

## Live dashboard

Open the published dashboard (GitHub Pages):

- https://gera9999.github.io/business-sales-analytics-dashboard/docs/

If the link shows a 404, GitHub Pages may not be enabled yet. See “View the dashboard on GitHub (no local Python)” below.

Note: if your root URL `https://gera9999.github.io/business-sales-analytics-dashboard/` shows the README instead of the dashboard, set GitHub Pages to serve from `/docs` (Settings → Pages). Then the root URL will render the dashboard.

It covers:
- Data loading & cleaning (schema normalization + date parsing)
- Executive KPIs (revenue, orders, customers, AOV, shipping time)
- Product, customer, geographic, and shipping performance analytics
- 7-day time-series forecasting (Prophet when available; simple fallback otherwise)
- Auto-generated business insights (text summary)

## Dataset

- Source file: `train.csv` (repo root)
- Canonical pipeline input: `data/train.csv` (auto-copied from root by `main.py`)

This dataset does **not** include Profit/Discount/Quantity. The analysis is intentionally designed around revenue (Sales), customers, geography, shipping, and time.

Expected columns include (names in the raw CSV):
- Order and shipment: `Order ID`, `Order Date`, `Ship Date`, `Ship Mode`
- Customer: `Customer ID`, `Customer Name`, `Segment`
- Geography: `Country`, `City`, `State`, `Postal Code`, `Region`
- Product: `Product ID`, `Category`, `Sub-Category`, `Product Name`
- Metric: `Sales`

## What it generates

### Analytics pipeline
The pipeline:
- Normalizes column names to `snake_case`
- Parses `order_date` and `ship_date`
- Coerces `sales` into numeric
- Computes `shipping_time_days = ship_date - order_date` (with basic guards)

### Dashboard (HTML)
Running the project generates an interactive dashboard at:

- `output/sales_dashboard.html`

Dashboard sections:
- **Key Metrics**: Total Revenue, Orders, Unique Customers, Average Order Value, Avg Shipping Time
- **Sales Performance**: daily trend, monthly trend, 7-day forecast
- **Product Analysis**: category/sub-category performance, top products table
- **Customer Analysis**: revenue by segment, top customers table
- **Geographic Analysis**: revenue by region + top states/cities
- **Shipping Analysis**: shipping time by ship mode and by region
- **Auto Insights**: short executive summary (e.g., “Top region”, “Best category”) with currency formatting ($12,500 / $250K / $1.5M)

## Project structure

```
business-sales-analytics-dashboard/
  data/
    train.csv
  notebooks/
    exploratory_analysis.ipynb
  src/
    customer_analysis.py
    data_loader.py
    forecasting.py
    insights.py
    kpi_analysis.py
    pipeline.py
    sales_analysis.py
    shipping_analysis.py
    __init__.py
  dashboard/
    __init__.py
    plotly_dashboard.py
  output/
    sales_dashboard.html
  main.py
  requirements.txt
  README.md
  train.csv
```

## Quickstart (Windows PowerShell)

1) Create & activate a virtual environment

```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

Optional (developer tools: linting/tests):

```powershell
pip install -r requirements-dev.txt
```

3) Run the pipeline + dashboard build

```powershell
python main.py
```

4) Open the dashboard

- `output/sales_dashboard.html`

## View the dashboard on GitHub (no local Python)

This repo also writes a static copy to `docs/index.html` (updated every time you run `python main.py`).
To let viewers open it directly from GitHub:

1) Commit and push the repository (including `docs/index.html`)
2) In GitHub: **Settings → Pages**
3) Set **Source** to: “Deploy from a branch”
4) Select **Branch**: `main` and **Folder**: `/docs`

After that, GitHub will publish a public URL where the dashboard can be opened in the browser.

## Notes

- Forecasting uses Prophet if installed and working. If not, the pipeline automatically falls back to a lightweight baseline forecast.
- The dashboard is designed to be readable and “executive-friendly”: sorted views, compact tables, and short currency formatting ($K/$M).
