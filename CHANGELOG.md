# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [0.2.0] — 2026-04-07

### Added

- **Operations Monitor dashboard** (`apps/operations_monitor/`)
  - New DQ check monitoring dashboard for operational teams
  - KPI cards: Total Checks, Pass Rate, Active Failures, Resolved Issues, Avg Resolution Time
  - Status heatmap grid: check × date colour-coded PASS/FAIL view
  - Daily trend: stacked bar chart of pass/fail counts over time
  - Failure lifecycle: side-by-side donut charts for Revenue and EPM lifecycle states
  - Resolution times: horizontal bar chart showing average fix time per check
  - Active failures table: action-required detail rows with status badges
  - Brand & wallet breakdown: grouped bar charts by dimension
  - Sidebar filters: Brand, Wallet Type, Check Name, Status View (Overall/Revenue/EPM)
  - Light/dark theme support (consistent with hub and other dashboards)
  - Data source: CSV for local dev, Databricks view for production (`global_vw_dq_monitor`)

- **Heatmap chart component** (`flutter_dash/components/charts.py`)
  - New `heatmap_chart()` function for status grids and intensity matrices
  - Fully theme-aware with configurable colorscale, hover templates, and auto-sizing
  - Exported from `flutter_dash.components` for use in any dashboard

- **Hub registration**
  - Operations Monitor added to `hub/hub_config.py` as a live dashboard (port 8505)
  - `scripts/run_local.ps1` updated to launch all 3 apps

- **README** updated with Operations Monitor in architecture diagram, repo structure, and quick start

### Changed

- `flutter_dash/components/__init__.py` — exports `heatmap_chart` alongside existing chart types

---

## [0.1.0] — 2026-03-01

Initial release of the FBI Hub platform.

### Added

- **FBI Hub** (`hub/`)
  - Tile-based launcher with search and theme toggle
  - App registry (`hub_config.py`) for managing dashboards
  - Light/dark theme passed to child apps via URL query parameter

- **Group Executive Report** (`apps/group_executive_report/`)
  - Multi-brand, multi-product performance dashboard
  - KPI cards with TY vs LY vs Budget variance and driver flip panels
  - Daily trend line chart with rich multi-series tooltips
  - Brand/product breakdown grouped bar charts
  - Composition pie/donut chart and waterfall bridge chart
  - Hierarchical financial data table with variance sub-columns
  - Sidebar: period picker, dimension filters, metric picker, grouping picker

- **flutter_dash shared library**
  - Theme system: `ThemeTokens` dataclass, `FLUTTER_DARK` and `FLUTTER_LIGHT` palettes
  - CSS generator and Plotly layout builder (auto-adapt to active theme)
  - Components: `kpi_card`, `line_chart`, `bar_chart`, `pie_chart`, `waterfall_chart`
  - `data_table` — hierarchical table with variance columns
  - `section_title` and `multi_section_title` — styled section headers
  - `SidebarBuilder` — composable sidebar with period picker, filters, theme toggle
  - Data utilities: `CsvLoader`, `DatabricksLoader`, filtering, aggregation, date helpers
  - Formatters: `fmt_currency` (£1.23M), `fmt_pct` (12.50%), `fmt_number`, `fmt_table_thousands`
  - Helpers: `MetricDef`, `SeriesStyle`, `Comparison`, `delta_colour`, `delta_arrow`
  - Integration stubs: Databricks SQL connector, Genie AI

- **Local development**
  - `scripts/run_local.ps1` — launches Hub and dashboards with one command
  - Root `app.py` redirector for backward compatibility
  - `pyproject.toml` for pip-installable `flutter_dash` package
