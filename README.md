# Flutter Dash

Reusable Streamlit dashboard framework for Flutter UK&I finance reporting.

## What is this?

`flutter_dash` is a Python package that provides:

- **Theme system** — consistent dark/light palettes with one-call setup
- **Component library** — KPI cards, line/bar/pie/waterfall charts, data tables, sidebar builder
- **Data layer** — date helpers, generic filtering, metric aggregation (sum + weighted avg)
- **Integrations** — Databricks Unity Catalog connector + Genie AI chat (stubs ready)
- **Finance conventions** — currency formatting, variance analysis (YoY, vs Budget), signed deltas

## Quick Start

### 1. Install

```bash
# From GitHub (private repo)
pip install git+https://github.com/YOUR_ORG/flutter-dash.git

# Or for local development (editable install)
pip install -e .
```

### 2. Create a Dashboard

Copy `dashboards/analytics/` as a template:

```
my_new_dashboard/
├── config.py          # Define YOUR metrics, drivers, dimensions
├── data_loader.py     # Point to YOUR data source (CSV or Databricks)
├── sections/          # Build YOUR page sections
│   ├── kpi_section.py
│   ├── trend_section.py
│   └── ...
└── app.py             # ~60 line orchestrator
```

### 3. Edit `config.py`

Define your metrics using `MetricDef`:

```python
from flutter_dash.helpers import MetricDef
from flutter_dash.formatters import fmt_currency, fmt_pct

REVENUE = MetricDef(
    label="Revenue",
    ty_col="revenue",           # Column name in your data
    ly_col="revenue_ly",
    bud_col="revenue_budget",
    formatter=fmt_currency,     # How to display it
)

MARGIN = MetricDef(
    label="Margin %",
    ty_col="margin",
    ly_col="margin_ly",
    bud_col="margin_budget",
    formatter=fmt_pct,
    is_pct=True,                # Uses weighted average, not sum
    weight_col="stakes",        # Weight column for averaging
)
```

### 4. Edit `data_loader.py`

```python
# For local CSV development:
DATA_SOURCE = "csv"
LOADER_KWARGS = {"file_path": "my_data.csv"}

# For Databricks Apps production:
DATA_SOURCE = "databricks"
LOADER_KWARGS = {
    "catalog": "my_catalog",
    "schema": "gold",
    "table": "daily_performance",
}
```

### 5. Write `app.py`

```python
import streamlit as st
from flutter_dash.theme import apply_theme
from flutter_dash.theme.palettes import FLUTTER_DARK

apply_theme(st, FLUTTER_DARK, page_title="My Dashboard")

df = load_data()
selections = build_sidebar(df)
df_filtered = filter_df(df, ...)

render_kpi_section(df_filtered, ...)
render_trend_section(df, ...)
```

### 6. Run

```bash
python -m streamlit run app.py
```

## Project Structure

```
flutter_dash/               # The shared package (pip-installable)
├── theme/                   # Palettes, CSS, Plotly layouts
├── components/              # KPI cards, charts, tables, sidebar
├── data/                    # Filtering, aggregation, loaders
├── integrations/            # Databricks, Genie AI
├── formatters.py            # fmt_currency, fmt_pct, fmt_number
└── helpers.py               # Dataclasses: MetricDef, Comparison, SeriesStyle

dashboards/                  # Dashboard instances (not part of the package)
└── analytics/               # The analytics dashboard
    ├── config.py            # Metric definitions, drivers, dimensions
    ├── data_loader.py       # CSV / Databricks loader config
    └── sections/            # Page sections (header, KPIs, charts, table)
```

## Key Concepts

### MetricDef
Tells the framework about a metric: what columns to use, how to format it, whether it's a percentage.

### Comparison
Represents a variance row (vs LY, vs Budget). KPI cards accept a list of these.

### SeriesStyle
Controls how a chart series looks (label, colour, dash pattern). Colours auto-fill from the theme if omitted.

### SidebarBuilder
Composable sidebar — chain `.add_header()`, `.add_period_picker()`, `.add_multiselect()`, `.render()`.

## Dependencies

- `streamlit >= 1.32.0`
- `pandas >= 2.0.0`
- `plotly >= 5.18.0`

Optional:
- `databricks-sql-connector >= 3.0.0` (for Databricks Apps deployment)
