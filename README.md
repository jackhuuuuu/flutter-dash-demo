# FBI Hub — Flutter Financial BI Platform

Multi-app dashboard platform for Flutter UK&I, powered by Streamlit and Databricks Apps.

## What is this?

This repo contains the **FBI Hub** (a landing page) and individual dashboard/app projects,
all sharing the `flutter_dash` Python package for consistent theming, components, and data utilities.

Each app is **independently deployable** as a Databricks App — if one app has an issue,
the others keep running. The hub links them together with search, theming, and discoverability.

---

## Repo Structure

```
├── flutter_dash/                        # Shared package (pip-installable)
│   ├── theme/                           #   Palettes, CSS, Plotly layouts
│   ├── components/                      #   KPI cards, charts, tables, sidebar
│   ├── data/                            #   Filtering, aggregation, loaders
│   ├── integrations/                    #   Databricks connector, Genie AI
│   ├── formatters.py                    #   fmt_currency, fmt_pct, fmt_number
│   └── helpers.py                       #   MetricDef, Comparison, SeriesStyle
│
├── hub/                                 # FBI Hub (Databricks App #1)
│   ├── app.py                           #   Landing page
│   ├── hub_config.py                    #   App registry (add new apps here)
│   ├── app.yaml                         #   Databricks Apps config
│   ├── assets/flutter_logo.png          #   Flutter logo
│   └── requirements.txt
│
├── apps/                                # Dashboard apps (one folder = one app)
│   └── group_executive_report/          # Group Executive Report (App #2)
│       ├── app.py                       #   Dashboard entry point
│       ├── config.py                    #   Metrics, drivers, dimensions
│       ├── data_loader.py               #   CSV / Databricks loader config
│       ├── sections/                    #   Page sections (header, KPIs, charts)
│       ├── sample_data.csv              #   Dev data (not used in production)
│       ├── app.yaml                     #   Databricks Apps config
│       └── requirements.txt
│
├── scripts/
│   └── run_local.ps1                    # Start all apps locally
│
├── pyproject.toml                       # flutter_dash package definition
└── .gitignore
```

---

## Quick Start (Local Development)

### 1. Clone and install

```bash
git clone https://github.com/jackhuuuuu/flutter-dash-demo.git
cd flutter-dash-demo

# Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate    # macOS/Linux

# Install flutter_dash in editable mode
pip install -e .
```

### 2. Run all apps

```powershell
# Start FBI Hub (port 8501) and Group Executive Report (port 8502)
.\scripts\run_local.ps1
```

Or run individually:

```powershell
cd hub
streamlit run app.py --server.port 8501

# In a separate terminal:
cd apps/group_executive_report
streamlit run app.py --server.port 8502
```

### 3. Open in browser

- **FBI Hub**: http://localhost:8501
- **Group Executive Report**: http://localhost:8502

---

## Creating a New Dashboard

### 1. Copy the template

```powershell
Copy-Item -Recurse apps/group_executive_report apps/my_new_dashboard
```

### 2. Edit `config.py`

Define your metrics, dimensions, and drivers:

```python
from flutter_dash.helpers import MetricDef
from flutter_dash.formatters import fmt_currency, fmt_pct

PAGE_TITLE = "My New Dashboard"
DASHBOARD_HEADING = "My New Dashboard"

REVENUE = MetricDef(
    label="Revenue",
    ty_col="revenue",           # Column name in your data
    ly_col="revenue_ly",
    bud_col="revenue_budget",
    formatter=fmt_currency,
)
```

### 3. Edit `data_loader.py`

```python
# For local CSV development:
DATA_SOURCE = "csv"
LOADER_KWARGS = {"file_path": "sample_data.csv"}

# For Databricks production:
# DATA_SOURCE = "databricks"
# LOADER_KWARGS = {"catalog": "my_catalog", "schema": "gold", "table": "my_table"}
```

### 4. Register in the hub

Add your app to `hub/hub_config.py`:

```python
{
    "id": "my_new_dashboard",
    "title": "My New Dashboard",
    "description": "What this dashboard does.",
    "icon": "📈",
    "section": "dashboards",
    "status": "live",
    "local_port": 8503,                    # Pick an unused port
    "app_path": "apps/my_new_dashboard",
    "internal": True,
},
```

### 5. Create `app.yaml`

Copy from an existing app — this tells Databricks how to run it
and lets the CI/CD pipeline detect changes.

### 6. Run and test

```powershell
cd apps/my_new_dashboard
streamlit run app.py --server.port 8503
```

---

## Deployment (Databricks Apps via GitHub Actions)

Each app is deployed independently via the CI/CD pipeline:

1. **Change detection** — the pipeline scans for folders containing `app.yaml`
   and only deploys apps whose files have changed.
2. **Workspace upload** — app files are uploaded to a Databricks workspace folder.
3. **App deploy** — `databricks apps deploy` creates/updates the Databricks App.
4. **Permissions** — access control is set per-app (teams, service principals).

The `flutter_dash` package is installed via `requirements.txt` in each app.
For production, point to the package from your private index or Git URL:

```
# In each app's requirements.txt:
flutter-dash @ git+https://github.com/jackhuuuuu/flutter-dash-demo.git
```

To add a new app to the deployment pipeline, add a step in your workflow YAML
following the same pattern as existing apps (workspace upload → deploy → permissions).

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **MetricDef** | Defines a metric: column names for TY/LY/Budget, formatter, percentage flag |
| **Comparison** | Variance row (vs LY, vs Budget) displayed on KPI cards |
| **SeriesStyle** | Chart series appearance (label, colour, dash). Auto-fills from theme if omitted |
| **SidebarBuilder** | Composable sidebar: `.add_header()`, `.add_period_picker()`, `.add_multiselect()`, `.render()` |
| **ThemeTokens** | Complete visual identity: backgrounds, text, semantic colours, chart palette |

## Theme System

- Default theme: **Flutter Light** (`FLUTTER_LIGHT`)
- Dark theme: **Flutter Dark** (`FLUTTER_DARK`)
- Theme toggle available in the hub and each dashboard sidebar
- Hub passes theme to dashboards via URL parameter `?theme=light|dark`

## Dependencies

- `streamlit >= 1.32.0`
- `pandas >= 2.0.0`
- `plotly >= 5.18.0`

Optional:
- `databricks-sql-connector >= 3.0.0` (for Databricks Apps deployment)
