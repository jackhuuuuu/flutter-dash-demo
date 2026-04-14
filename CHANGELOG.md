# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [0.4.0] — 2026-04-14

### Added

- **Per-tab sidebar filters** — sidebar now shows tab-specific filters:
  - File Delivery tab: File Name multiselect, Delivery Lifecycle selector
  - Check Detail tab: Check Name multiselect, Table View mode (All/Failed/Passed)
- **ERP Resends KPI** — new card showing count of files re-sent after initial ERP
- **3-level file heatmap** — green (0d on-time), yellow (D+1), red (>1d late),
  grey (no data); purely colour-based, no cell text
- **`show_text` parameter** on `heatmap_chart()` — toggleable cell labels for
  modular reuse across dashboards
- **Tab styling** — CSS for `st.tabs` ensuring unselected tabs are visible in
  both light and dark themes
- **Check table view modes** — "All", "Failed Only", "Passed Only" via sidebar

### Changed

- **File delivery uses `erp_final_delivered_at`** — ERP delivery rate, delivery
  days, and heatmap all use the final ERP delivery timestamp (not first)
- **Resolution columns renamed** — `_minutes` → `_hours` in both views;
  removed `/60` conversions throughout
- **File KPIs reworked** — removed "Total Files" card, replaced "Avg Delivery Days"
  with "Late Deliveries" (files >1 day) and "ERP Resends"
- **Check KPIs reworked** — removed "Total Checks" card, added separate Revenue
  and EPM pass rate cards
- **Check tab simplified** — removed trend, lifecycle, resolution, and brand
  breakdown sections; now shows KPIs + heatmap + detail table
- **Heatmaps cleaned up** — removed PASS/FAIL text labels from cells in both
  file and check heatmaps; info shown in tooltip only
- **Check detail table** — removed Wallet column, accepts `view_mode` parameter

### Fixed

- **GER flip KPI button** — added `min-height` and explicit `height` on
  `st.html()` so the iframe is tall enough for the flipped (driver) view
- **Light theme tab visibility** — unselected tabs now use `text_muted` colour
  instead of invisible white-on-white

---

## [0.3.0] — 2026-04-10

### Added

- **Operations Monitor: File Delivery tab** — new front page showing file-level
  delivery status (ERP/EPM/Manual Override) across brands and dates
  - KPI cards: Total Files, ERP Delivery Rate, EPM Only, Manual Overrides, Avg Delivery Days
  - File delivery heatmap: file × date colour grid
  - File delivery detail table with lifecycle badges
  - Data source: `global_vw_file_delivery` view

- **Tab navigation** — Operations Monitor now uses `st.tabs` for two-level view:
  - Tab 1 "File Delivery": high-level file status (designed for at-a-glance monitoring)
  - Tab 2 "Check Detail": granular DQ check results (drill-down for investigation)

- **Check-to-file mapping** (`global_dq_check_file_mapping.csv`) — loaded as bridge
  between file-level and check-level views

- **Check value tooltips** — check detail table now shows daily/MTD values and
  revenue/EPM tolerances on hover over the check name

### Changed

- **Operations Monitor data loader** — now loads three datasets (file delivery,
  DQ monitor, check-file mapping) instead of a single checks log
- **DQ monitor sample data** updated with check values and tolerance columns
  (`check_daily_value`, `check_mtd_value`, `daily_revenue_tolerance`, etc.)
- **Sidebar simplified** — removed Wallet Type and Check Name filters from sidebar
  (check-level filtering happens within the Check Detail tab)

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
