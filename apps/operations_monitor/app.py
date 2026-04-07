# apps/operations_monitor/app.py
"""
Operations Monitor — Flutter UK&I
Data Quality Checks | Pipeline Health

This is the main orchestrator for the Operations Monitor dashboard.
It wires together:
  - flutter_dash package   → theme, components, data utilities
  - config.py              → column names, status values, page settings
  - data_loader.py         → CSV or Databricks data source
  - sections/              → each visual section of the dashboard

The dashboard is designed for operational teams (including non-technical
users) to monitor:
  - DQ check pass/fail status across brands and dates
  - Failure resolution tracking and response times
  - (Future) Databricks job/pipeline performance

Sidebar selections flow into each section:
  - Brand / Wallet Type multiselects    → dimension filtering
  - Check Name multiselect              → drill-down to specific checks
  - Status Type toggle                  → Revenue / EPM / Overall view
  - Date range                          → date window filtering

Run locally:
    cd apps/operations_monitor
    streamlit run app.py --server.port 8505
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import apply_theme
from flutter_dash.theme.palettes import FLUTTER_DARK, FLUTTER_LIGHT
from flutter_dash.components.sidebar import SidebarBuilder

from config import (
    PAGE_TITLE, PAGE_ICON, DASHBOARD_HEADING, DASHBOARD_SUBTITLE,
    COL_REPORTING_DATE, COL_BRAND, COL_WALLET_TYPE, COL_CHECK_NAME,
    COL_OVERALL_STATUS, COL_LATEST_RUN,
    DIMENSIONS, STATUS_TYPES,
)
from data_loader import load_data
from sections import (
    render_header,
    render_kpi_section,
    render_heatmap,
    render_trend_section,
    render_lifecycle_section,
    render_resolution_section,
    render_detail_table,
    render_brand_breakdown,
)


# ══════════════════════════════════════════════════════════════════════════════
# THEME SETUP
# ══════════════════════════════════════════════════════════════════════════════
# Read theme from URL query param (passed from Hub) or default to light.
# Once in session_state, user can toggle independently via sidebar button.

if "theme" not in st.session_state:
    theme_param = st.query_params.get("theme", "light")
    st.session_state.theme = theme_param if theme_param in ("light", "dark") else "light"

_palette = FLUTTER_LIGHT if st.session_state.theme == "light" else FLUTTER_DARK
apply_theme(st, _palette, page_title=PAGE_TITLE, page_icon=PAGE_ICON)


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

df_raw = load_data()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

sidebar = SidebarBuilder(st)
sidebar.add_header(PAGE_TITLE, DASHBOARD_SUBTITLE)
sidebar.add_theme_toggle()
sidebar.add_divider()

# ── Dimension filters (Brand, Wallet Type) ────────────────────────────────
all_values = {}
for col, label in DIMENSIONS.items():
    values = sorted(df_raw[col].unique())
    all_values[label] = values
    sidebar.add_multiselect(label, values, placeholder=f"All {label}s")

# ── Check Name filter ─────────────────────────────────────────────────────
all_checks = sorted(df_raw[COL_CHECK_NAME].unique())
sidebar.add_multiselect("Check Name", all_checks, placeholder="All Checks")

sidebar.add_divider()

# ── Status type picker (Overall / Revenue / EPM) ─────────────────────────
# We add this as a custom selectbox via the sidebar render loop.
# For now we use the metric picker slot to hold this.
sidebar.add_metric_picker(
    list(STATUS_TYPES.keys()),
    label="Status View",
)

sidebar.add_divider()

# ── Footer with data freshness ────────────────────────────────────────────
latest_run = None
if COL_LATEST_RUN in df_raw.columns:
    latest_run_val = df_raw[COL_LATEST_RUN].dropna()
    if len(latest_run_val) > 0:
        latest_run = str(latest_run_val.iloc[0])[:19].replace("T", " ")

sidebar.add_footer(f"Latest run: {latest_run or 'Unknown'}")

selections = sidebar.render()


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACT SIDEBAR SELECTIONS
# ══════════════════════════════════════════════════════════════════════════════

# Dimension filters
sel_brands = selections.get("Brand", all_values.get("Brand", []))
sel_wallets = selections.get("Wallet Type", all_values.get("Wallet Type", []))
sel_checks = selections.get("Check Name", all_checks)

# Status view type
sel_status_label = selections.get("metric", "Overall")
sel_status_col = STATUS_TYPES.get(sel_status_label, COL_OVERALL_STATUS)

# Build display labels for the header
brand_label = (
    ", ".join(sel_brands)
    if len(sel_brands) < len(all_values.get("Brand", []))
    else "All Brands"
)
wallet_label = (
    ", ".join(sel_wallets)
    if len(sel_wallets) < len(all_values.get("Wallet Type", []))
    else "All Wallet Types"
)


# ══════════════════════════════════════════════════════════════════════════════
# FILTER DATA
# ══════════════════════════════════════════════════════════════════════════════

df_filtered = df_raw.copy()

# Apply dimension filters
df_filtered = df_filtered[df_filtered[COL_BRAND].isin(sel_brands)]
df_filtered = df_filtered[df_filtered[COL_WALLET_TYPE].isin(sel_wallets)]
df_filtered = df_filtered[df_filtered[COL_CHECK_NAME].isin(sel_checks)]

# Date range for header display
if not df_filtered.empty:
    min_date = min(df_filtered[COL_REPORTING_DATE])
    max_date = max(df_filtered[COL_REPORTING_DATE])
    date_range = (
        f"{min_date.strftime('%d %b')} – {max_date.strftime('%d %b %Y')}"
        if hasattr(min_date, "strftime")
        else f"{min_date} – {max_date}"
    )
else:
    date_range = "No data"


# ══════════════════════════════════════════════════════════════════════════════
# RENDER DASHBOARD SECTIONS
# ══════════════════════════════════════════════════════════════════════════════

# 1. Header — title, filters, data freshness
render_header(
    title=DASHBOARD_HEADING,
    subtitle=DASHBOARD_SUBTITLE,
    brand_label=brand_label,
    wallet_label=wallet_label,
    latest_run=latest_run,
    date_range=date_range,
)

# 2. KPI Cards — headline operational metrics
render_kpi_section(df_filtered)

# 3. Status Heatmap — check × date colour grid
render_heatmap(df_filtered, status_col=sel_status_col, status_label=sel_status_label)

# 4. Daily Trend — pass/fail bar chart over time
render_trend_section(df_filtered, status_col=sel_status_col, status_label=sel_status_label)

# 5. Failure Lifecycle — donut charts for revenue & EPM lifecycle states
# 6. Resolution Times — horizontal bar chart of avg resolution per check
col_lifecycle, col_resolution = st.columns(2)
with col_lifecycle:
    render_lifecycle_section(df_filtered)
with col_resolution:
    render_resolution_section(df_filtered)

# 7. Active Failures Table — action-required detail rows
render_detail_table(df_filtered)

# 8. Brand & Wallet Breakdown — grouped bar charts by dimension
render_brand_breakdown(df_filtered)
