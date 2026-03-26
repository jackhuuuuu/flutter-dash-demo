# FBI Hub — Flutter Financial BI Platform

A multi-app dashboard platform for Flutter UK&I, powered by **Streamlit**.  
Think of it as a home page (the "Hub") that links to all your team's dashboards and analytics apps.

## What is this?

| What | Where |
|------|-------|
| **FBI Hub** (home page) | [hub/](hub/) |
| **Group Executive Report** (first dashboard) | [apps/group_executive_report/](apps/group_executive_report/) |
| **Shared styling & components** | [flutter_dash/](flutter_dash/) |

Each dashboard is **independent** — if one has a problem, the others keep running.  
The hub connects them together with **search**, **light/dark theming**, and a tile-based launcher.

### Live links (Streamlit Cloud)

| App | URL |
|-----|-----|
| FBI Hub | *(deploy from `hub/app.py`)* |
| Group Executive Report | https://flutter-dash-demo-nip8zbftupozngv5a28zna.streamlit.app |

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

> **Prerequisites**: You need [Python 3.10+](https://www.python.org/downloads/) installed.  
> If you're not sure, open a terminal and type `python --version`.

### 1. Clone and install

```bash
git clone https://github.com/jackhuuuuu/flutter-dash-demo.git
cd flutter-dash-demo

# Create a virtual environment (keeps packages isolated from your system)
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1   # Windows (PowerShell)
# source .venv/bin/activate    # macOS / Linux

# Install the shared flutter_dash package
pip install -e .
```

### 2. Run all apps with one command

```powershell
.\scripts\run_local.ps1
```

This script will:
- **Auto-kill** any stale processes on the dashboard ports
- Start the FBI Hub on **http://localhost:8501**
- Start the Group Executive Report on **http://localhost:8502**
- Press **Ctrl+C** to stop everything cleanly

> **Tip**: If the script fails because a port is busy, just run it again — it cleans up automatically.

### 3. Or run apps individually

Open **two separate terminals**, activate the venv in each, then:

```powershell
# Terminal 1 — Hub
cd hub
streamlit run app.py --server.port 8501

# Terminal 2 — Dashboard
cd apps/group_executive_report
streamlit run app.py --server.port 8502
```

### 4. Open in your browser

| App | Local URL |
|-----|-----------|
| FBI Hub | http://localhost:8501 |
| Group Executive Report | http://localhost:8502 |

When you click **"Launch →"** on a tile in the hub, it automatically opens the correct app —  
locally it connects to `localhost`, on Streamlit Cloud it connects to the deployed URL.

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
    "cloud_url": "",                       # Fill in after deploying to Streamlit Cloud
    "internal": True,
},
```

Also add it to `scripts/run_local.ps1` so the script starts it automatically:

```powershell
$apps = @(
    # ... existing apps ...
    @{ Port = 8503; Name = "My New Dashboard"; Path = "apps/my_new_dashboard" }
)
```

### 5. Add the `cloud_url` (for Streamlit Cloud)

If you're deploying to Streamlit Cloud, add the deployed URL so the hub can link to it:

```python
    "cloud_url": "https://your-app-name.streamlit.app",
```

When running locally, this is ignored — the hub uses `localhost:<port>` instead.

### 6. Create `app.yaml`

Copy from an existing app — this tells Databricks how to run it
and lets the CI/CD pipeline detect changes.

### 7. Run and test

```powershell
cd apps/my_new_dashboard
streamlit run app.py --server.port 8503
```

---

## Deployment

### Streamlit Community Cloud (free)

The simplest way to share dashboards with your team:

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **"New app"** and fill in:

   | Field | Hub | Dashboard |
   |-------|-----|-----------|
   | Repository | `jackhuuuuu/flutter-dash-demo` | `jackhuuuuu/flutter-dash-demo` |
   | Branch | `main` | `main` |
   | Main file path | `hub/app.py` | `apps/group_executive_report/app.py` |

3. After deployment, copy the dashboard's URL and paste it into `hub/hub_config.py`  
   as the `cloud_url` value. Commit, push, and the hub will auto-redeploy.

> **How it works**: The hub auto-detects whether it's running locally or on Streamlit Cloud.  
> Locally → links go to `localhost:<port>`. On the cloud → links use `cloud_url`.

### Databricks Apps (enterprise)

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

---

## Key Concepts (glossary)

New to the codebase? Here's what the main building blocks mean:

| Term | What it is | Where it lives |
|------|-----------|----------------|
| **MetricDef** | A "recipe" for a metric — which columns to use for This Year / Last Year / Budget, and how to format numbers | `config.py` in each app |
| **Comparison** | A variance row shown on KPI cards (e.g. "+5% vs LY") | Used inside KPI sections |
| **SeriesStyle** | How a line/bar looks on a chart (label, colour, dashed/solid). Fills in automatically from the theme if you don't set it | `flutter_dash/helpers.py` |
| **SidebarBuilder** | A helper to build the sidebar step by step: `.add_header()` → `.add_period_picker()` → `.add_multiselect()` → `.render()` | `flutter_dash/components/sidebar.py` |
| **ThemeTokens** | The full "visual identity" — background colours, text colours, accent, chart palette. Two built-in themes: Light and Dark | `flutter_dash/theme/palettes.py` |

## Theme System

- Default theme: **Flutter Light** (`FLUTTER_LIGHT`)
- Dark theme: **Flutter Dark** (`FLUTTER_DARK`)
- A 🌙/☀️ toggle button in the hub and each dashboard switches between them
- The hub passes the chosen theme to dashboards via URL parameter `?theme=light|dark`
- Charts, KPI cards, tables, and sidebar all adapt automatically

## Hub Features

- **Search**: Type in the search bar and results filter instantly as you type.  
  Deleting characters shows more results. Clear the bar to see everything.
- **Theme toggle**: Click 🌙/☀️ to switch light/dark. The theme carries over when you launch a dashboard.
- **App tiles**: Each app shows its status (● Live or ◌ Coming Soon) with a launch link.

## Dependencies

- `streamlit >= 1.32.0`
- `pandas >= 2.0.0`
- `plotly >= 5.18.0`

Optional:
- `databricks-sql-connector >= 3.0.0` (for Databricks deployment)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Run `.\scripts\run_local.ps1` — it auto-kills stale processes |
| `ModuleNotFoundError: flutter_dash` | Run `pip install -e .` from the repo root |
| Dashboard shows "Coming Soon" | Check `hub/hub_config.py` — set `"status": "live"` |
| Theme not carrying over to dashboard | Make sure `"internal": True` is set in hub_config |
| Search bar not filtering live | Hard-refresh the browser (`Ctrl+Shift+R`) to reload JS |
