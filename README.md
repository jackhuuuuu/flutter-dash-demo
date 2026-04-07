# FBI Hub — Flutter Financial BI Platform

A multi-app dashboard platform for Flutter UK&I, powered by **Streamlit** and deployable on **Databricks Apps**.

The platform consists of:
- A **Hub** (landing page) that connects all dashboards via a searchable tile launcher
- **Individual dashboards** that each run independently (if one breaks, nothing else is affected)
- A **shared component library** (`flutter_dash`) providing themed charts, KPI cards, tables, and more

---

## How It All Fits Together

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FBI Hub (hub/app.py)                         │
│  Tile-based launcher with search, light/dark theming, app registry │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│   │  Group Executive  │  │   Operations     │  │   P&L Dashboard  │ │
│   │     Report ✅     │  │   Monitor ✅     │  │   (Coming Soon)  │ │
│   └────────┬─────────┘  └────────┬─────────┘  └──────────────────┘ │
└────────────┼─────────────────────┼─────────────────────────────────┘
             │ uses
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   flutter_dash (shared package)                     │
│                                                                     │
│  theme/        → Light & dark palettes, CSS, Plotly chart layouts   │
│  components/   → KPI cards, line/bar/pie/waterfall/heatmap charts    │
│  data/         → Filters, aggregation, date helpers, data loaders   │
│  integrations/ → Databricks connector, Genie AI (stubs)             │
│  formatters.py → £1.23M, 12.50%, percentage-point formatting        │
│  helpers.py    → MetricDef, SeriesStyle, variance colour utilities   │
└─────────────────────────────────────────────────────────────────────┘
```

**Key concept**: Every dashboard imports from `flutter_dash` for its styling and components, so all apps look consistent. When you build a new dashboard, you focus on *what to show* (metrics, data) — not *how to style it*.

---

## Repo Structure

```
├── flutter_dash/                        # Shared package (pip-installable)
│   ├── theme/                           #   Palettes, CSS, Plotly layouts
│   │   ├── tokens.py                    #     ThemeTokens dataclass (colour contract)
│   │   ├── palettes.py                  #     FLUTTER_DARK and FLUTTER_LIGHT presets
│   │   ├── css.py                       #     Generates Streamlit CSS from tokens
│   │   └── plotly.py                    #     Base Plotly chart layout from tokens
│   ├── components/                      #   Reusable UI components
│   │   ├── kpi_card.py                  #     Metric card with variance comparisons
│   │   ├── charts.py                    #     Line, bar, pie, waterfall, heatmap charts
│   │   ├── data_table.py               #     Hierarchical financial data table
│   │   ├── section_title.py            #     Styled section headers
│   │   └── sidebar.py                  #     Composable sidebar builder
│   ├── data/                            #   Data utilities
│   │   ├── filters.py                   #     Generic DataFrame filtering
│   │   ├── aggregation.py              #     Metric aggregation, weighted averages
│   │   ├── date_helpers.py             #     Period date calculations
│   │   └── loader.py                   #     CSV and Databricks data loaders
│   ├── integrations/                    #   External service connectors
│   │   ├── databricks.py               #     Unity Catalog SQL connector
│   │   └── genie.py                    #     Genie AI chat & commentary (stub)
│   ├── formatters.py                    #   Number formatting (currency, %, pp)
│   └── helpers.py                       #   MetricDef, Comparison, SeriesStyle
│
├── hub/                                 # FBI Hub — landing page app
│   ├── app.py                           #   Main hub with search + tiles
│   ├── hub_config.py                    #   App registry (add new apps here!)
│   ├── app.yaml                         #   Databricks Apps deployment config
│   ├── assets/flutter_logo.png          #   Logo image
│   └── requirements.txt
│
├── apps/                                # Dashboard apps (one folder = one app)
│   └── group_executive_report/          #   Group Executive Report
│       ├── app.py                       #     Main orchestrator
│       ├── config.py                    #     Metrics, drivers, dimensions
│       ├── data_loader.py              #     Data source config (CSV / Databricks)
│       ├── sample_data.csv             #     Sample data for local development
│       ├── sections/                    #     Visual sections of the dashboard
│       │   ├── header.py               #       Title bar + filter summary
│       │   ├── kpi_section.py          #       KPI metric cards row
│       │   ├── trend_section.py        #       Daily trend line chart
│       │   ├── brand_breakdown.py      #       Grouped bar chart
│       │   ├── additional_charts.py    #       Pie chart + waterfall bridge
│       │   └── detail_table.py         #       Hierarchical data table
│       ├── app.yaml                     #     Databricks Apps config
│       └── requirements.txt
│
│   └── operations_monitor/              #   Operations Monitor (DQ checks)
│       ├── app.py                       #     Main orchestrator
│       ├── config.py                    #     Column mappings, status values
│       ├── data_loader.py              #     Data source config (CSV / Databricks)
│       ├── checks_log_sample.csv       #     Sample DQ check results
│       ├── sections/                    #     Visual sections of the dashboard
│       │   ├── header.py               #       Title bar + filter summary
│       │   ├── kpi_section.py          #       Operational health KPI cards
│       │   ├── heatmap.py              #       Check × date status grid
│       │   ├── trend_section.py        #       Daily pass/fail stacked bars
│       │   ├── lifecycle_section.py    #       Revenue & EPM lifecycle donuts
│       │   ├── resolution_section.py   #       Resolution time bar chart
│       │   ├── detail_table.py         #       Active failures action table
│       │   └── brand_breakdown.py      #       By brand/wallet grouped bars
│       ├── app.yaml                     #     Databricks Apps config
│       └── requirements.txt
│
├── scripts/
│   └── run_local.ps1                    # Start all apps locally with one command
│
├── app.py                               # Root redirector (launches hub for convenience)
├── pyproject.toml                       # flutter_dash package definition
├── requirements.txt                     # Root pip install (installs flutter_dash)
└── ideas.txt                            # Future improvement ideas
```

---

## Quick Start (Local Development)

> **Prerequisites**: [Python 3.10+](https://www.python.org/downloads/) installed.
> Check with `python --version` in a terminal.

### 1. Clone and install

```bash
git clone https://github.com/jackhuuuuu/flutter-dash-demo.git
cd flutter-dash-demo

# Create a virtual environment (keeps packages isolated)
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1   # Windows (PowerShell)
# source .venv/bin/activate    # macOS / Linux

# Install the shared flutter_dash package in development mode
pip install -e .
```

### 2. Run everything with one command

```powershell
.\scripts\run_local.ps1
```

This starts:
- **FBI Hub** → http://localhost:8501
- **Group Executive Report** → http://localhost:8502
- **Operations Monitor** → http://localhost:8505

Press **Ctrl+C** to stop all apps.

### 3. Or run apps individually

```powershell
# Terminal 1 — Hub
cd hub
streamlit run app.py --server.port 8501

# Terminal 2 — Dashboard
cd apps/group_executive_report
streamlit run app.py --server.port 8502

# Terminal 3 — Operations Monitor
cd apps/operations_monitor
streamlit run app.py --server.port 8505
```

---

## Creating a New Dashboard

Follow these steps to create a new dashboard and connect it to the hub.

### Step 1 — Copy the template

```powershell
Copy-Item -Recurse apps/group_executive_report apps/my_new_dashboard
```

### Step 2 — Define your metrics in `config.py`

Each metric is defined as a `MetricDef` — this tells the dashboard what columns to read, how to format values, and whether it's a percentage:

```python
from flutter_dash.helpers import MetricDef
from flutter_dash.formatters import fmt_currency, fmt_pct

PAGE_TITLE = "My New Dashboard"

REVENUE = MetricDef(
    label="Revenue",          # Display name in the UI
    ty_col="revenue",         # This Year column in your DataFrame
    ly_col="revenue_ly",      # Last Year column
    bud_col="revenue_budget", # Budget column
    formatter=fmt_currency,   # How to format values (£1.23M)
)

# For percentage metrics like margin:
MARGIN = MetricDef(
    label="Margin %",
    ty_col="margin",
    ly_col="margin_ly",
    bud_col="margin_budget",
    formatter=fmt_pct,        # Formats as 12.50%
    is_pct=True,              # Deltas shown in percentage points (pp)
    weight_col="revenue",     # Weighted average by this column
)

KPI_METRICS = [REVENUE, MARGIN]
```

### Step 3 — Configure your data source in `data_loader.py`

```python
# For local development with a CSV file:
DATA_SOURCE = "csv"
LOADER_KWARGS = {"file_path": "sample_data.csv"}

# For Databricks production:
# DATA_SOURCE = "databricks"
# LOADER_KWARGS = {
#     "catalog": "my_catalog",
#     "schema": "gold",
#     "table": "my_table",
# }
```

### Step 4 — Register in the hub

Add your app to `hub/hub_config.py`:

```python
{
    "id": "my_new_dashboard",
    "title": "My New Dashboard",
    "description": "What this dashboard does.",
    "icon": "📈",
    "section": "dashboards",
    "status": "live",
    "local_port": 8503,
    "app_path": "apps/my_new_dashboard",
    "internal": True,
},
```

### Step 5 — Add to the local runner

In `scripts/run_local.ps1`, add your app:

```powershell
$apps = @(
    @{ Port = 8501; Name = "FBI Hub";                Path = "hub" },
    @{ Port = 8502; Name = "Group Executive Report"; Path = "apps/group_executive_report" },
    @{ Port = 8503; Name = "My New Dashboard";       Path = "apps/my_new_dashboard" }
)
```

### Step 6 — Run and test

```powershell
.\scripts\run_local.ps1
```

Your new dashboard will appear at http://localhost:8503 and show up as a tile on the hub.

---

## Key Concepts

### Theme System

All visual styling flows from a single `ThemeTokens` dataclass. Two presets are included:
- `FLUTTER_DARK` — navy backgrounds, cyan accent
- `FLUTTER_LIGHT` — white/grey backgrounds, darker cyan accent

Switching themes is one line: `apply_theme(st, FLUTTER_LIGHT)`. Every component — charts, cards, tables, sidebar — automatically adapts.

### Sidebar Selections → Chart Parameters

The sidebar is built with `SidebarBuilder`, which returns a selections dict. The orchestrator (`app.py`) extracts values and passes them as function parameters to each section:

```
Sidebar widget          →  selections key   →  passed to sections as
──────────────────────────────────────────────────────────────────────
Period picker           →  "period"          →  period, period_start, period_end
Brand multiselect       →  "Brand"           →  brand filter + brand_label
Product multiselect     →  "Product"         →  product filter + product_label
Primary Metric picker   →  "metric"          →  sel_metric (MetricDef)
Chart Grouping picker   →  "grouping"        →  sel_grouping ("brand"/"product")
```

### MetricDef

The core concept for defining what metrics your dashboard shows. A `MetricDef` bundles:
- Column names (TY, LY, Budget)
- Formatting function
- Whether it's a percentage metric (uses weighted average instead of sum)

This means KPI cards, charts, and tables all know how to handle any metric without hardcoding.

---

## Deployment

### Streamlit Cloud

Each app can be deployed separately on [Streamlit Cloud](https://streamlit.io/cloud):
1. Point at the app's `app.py` (e.g. `apps/group_executive_report/app.py`)
2. Set the requirements file to the app's `requirements.txt`
3. Add the deployed URL as `cloud_url` in `hub_config.py`

### Databricks Apps

Each app folder has an `app.yaml` for Databricks Apps deployment. The hub detects the `DATABRICKS_APPS_BASE_URL` environment variable and generates correct links automatically.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI framework | [Streamlit](https://streamlit.io/) |
| Charts | [Plotly](https://plotly.com/python/) |
| Data | [Pandas](https://pandas.pydata.org/) |
| Shared library | `flutter_dash` (this repo) |
| Deployment | Databricks Apps / Streamlit Cloud |

---

## Live Dashboards

| Dashboard | Description | Status |
|-----------|-------------|--------|
| **Group Executive Report** | Multi-brand, multi-product performance with KPIs, trends, and variance analysis | ✅ Live |
| **Operations Monitor** | Data quality check monitoring with pass/fail heatmaps, failure lifecycle tracking, and resolution times | ✅ Live |
| **P&L Dashboard** | Profit & Loss reporting with drill-down by cost centre and entity | 🔜 Coming Soon |
| **Trading Dashboard** | Real-time trading metrics across sports and gaming products | 🔜 Coming Soon |
