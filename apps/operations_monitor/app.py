# apps/operations_monitor/app.py
"""
Operations Monitor — Flutter UK&I
File Delivery Status | Data Quality Checks

This is the main orchestrator for the Operations Monitor dashboard.
It wires together:
  - flutter_dash package   → theme, components, data utilities
  - config.py              → column names, status values, page settings
  - data_loader.py         → CSV or Databricks data source
  - sections/              → each visual section of the dashboard

The dashboard has two tabs:
  1. File Delivery — high-level view of which data files have been
     delivered and their ERP/EPM status.
  2. Check Detail — granular DQ check results with pass/fail status.

Each tab has its own sidebar filters that update independently.

Run locally:
    cd apps/operations_monitor
    streamlit run app.py --server.port 8505
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import apply_theme, get_active_theme
from flutter_dash.theme.palettes import FLUTTER_DARK, FLUTTER_LIGHT
from flutter_dash.theme.tokens import hex_to_rgba

from config import (
    PAGE_TITLE, PAGE_ICON, DASHBOARD_HEADING, DASHBOARD_SUBTITLE,
    COL_REPORTING_DATE, COL_BRAND, COL_FILE_NAME,
    COL_CHECK_NAME,
    COL_FILE_OVERALL_STATUS, COL_OVERALL_STATUS,
    COL_FILE_LATEST_RUN,
    COL_DELIVERY_LIFECYCLE,
    FILE_STATUS_TYPES, CHECK_STATUS_TYPES,
    DELIVERY_ERP_DELIVERED, DELIVERY_EPM_ONLY, DELIVERY_MANUAL_OVERRIDE,
)
from data_loader import load_file_delivery, load_dq_monitor, load_check_file_mapping
from sections import (
    render_header,
    render_file_kpi_section,
    render_file_heatmap,
    render_file_detail_table,
    render_kpi_section,
    render_heatmap,
    render_detail_table,
)


# ══════════════════════════════════════════════════════════════════════════════
# THEME SETUP
# ══════════════════════════════════════════════════════════════════════════════

if "theme" not in st.session_state:
    theme_param = st.query_params.get("theme", "light")
    st.session_state.theme = theme_param if theme_param in ("light", "dark") else "light"

_palette = FLUTTER_LIGHT if st.session_state.theme == "light" else FLUTTER_DARK
apply_theme(st, _palette, page_title=PAGE_TITLE, page_icon=PAGE_ICON)


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

df_files = load_file_delivery()
df_checks = load_dq_monitor()
df_mapping = load_check_file_mapping()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — per-tab filters
# ══════════════════════════════════════════════════════════════════════════════

tokens = get_active_theme()

with st.sidebar:
    # Header
    st.markdown(
        f"""
        <div style="padding:16px 0 24px;">
          <h1 style="color:{tokens.accent};font-size:22px;
                     font-weight:700;margin:0;">
            📊 {PAGE_TITLE}
          </h1>
          <p style="color:{tokens.text_muted};font-size:12px;margin:4px 0 0;">
            {DASHBOARD_SUBTITLE}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Theme toggle
    _is_dark = st.session_state.get("theme") == "dark"
    _icon = "☀️" if _is_dark else "🌙"
    if st.button(_icon, key="theme_toggle"):
        st.session_state.theme = "light" if _is_dark else "dark"
        st.rerun()

    st.markdown("---")

    # ── Shared: Brand filter ──────────────────────────────────────────────
    all_brands = sorted(df_files[COL_BRAND].unique())
    sel_brands = st.multiselect(
        "Brand", all_brands, default=all_brands, placeholder="All Brands",
    )
    if not sel_brands:
        sel_brands = list(all_brands)

    st.markdown("---")

    # ── File Delivery filters ─────────────────────────────────────────────
    st.markdown(
        f'<p style="color:{tokens.accent};font-size:12px;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:.08em;margin:0 0 8px;">'
        f'📁 File Delivery</p>',
        unsafe_allow_html=True,
    )

    # File name filter
    all_files = sorted(df_files[COL_FILE_NAME].unique())
    sel_files = st.multiselect(
        "File Name", all_files, default=all_files, placeholder="All Files",
        key="file_filter",
    )
    if not sel_files:
        sel_files = list(all_files)

    # Lifecycle filter
    lifecycle_options = ["All", "ERP_DELIVERED", "EPM_ONLY", "MANUAL_OVERRIDE"]
    sel_lifecycle = st.selectbox("Delivery Lifecycle", lifecycle_options, key="lifecycle_filter")

    # Status view for file heatmap
    sel_file_status_label = st.selectbox(
        "Status View",
        list(FILE_STATUS_TYPES.keys()),
        key="file_status_view",
    )

    st.markdown("---")

    # ── Check Detail filters ──────────────────────────────────────────────
    st.markdown(
        f'<p style="color:{tokens.accent};font-size:12px;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:.08em;margin:0 0 8px;">'
        f'🔍 Check Detail</p>',
        unsafe_allow_html=True,
    )

    # Check name filter
    all_checks = sorted(df_checks[COL_CHECK_NAME].unique())
    sel_checks = st.multiselect(
        "Check Name", all_checks, default=all_checks, placeholder="All Checks",
        key="check_filter",
    )
    if not sel_checks:
        sel_checks = list(all_checks)

    # Status view for check heatmap
    sel_check_status_label = st.selectbox(
        "Status View",
        list(CHECK_STATUS_TYPES.keys()),
        key="check_status_view",
    )

    # Check table view mode
    check_view_options = ["All", "Failed Only", "Passed Only"]
    sel_check_view = st.selectbox("Table View", check_view_options, key="check_table_view")

    st.markdown("---")

    # Data freshness
    latest_run = None
    if COL_FILE_LATEST_RUN in df_files.columns:
        latest_run_val = df_files[COL_FILE_LATEST_RUN].dropna()
        if len(latest_run_val) > 0:
            latest_run = str(latest_run_val.iloc[0])[:19].replace("T", " ")

    st.markdown(
        f'<p style="color:{tokens.text_muted};font-size:10px;">'
        f'Latest run: {latest_run or "Unknown"}</p>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAP STATUS SELECTIONS TO COLUMNS
# ══════════════════════════════════════════════════════════════════════════════

sel_file_status_col = FILE_STATUS_TYPES.get(sel_file_status_label, COL_FILE_OVERALL_STATUS)
sel_check_status_col = CHECK_STATUS_TYPES.get(sel_check_status_label, COL_OVERALL_STATUS)

brand_label = (
    ", ".join(sel_brands)
    if len(sel_brands) < len(all_brands)
    else "All Brands"
)


# ══════════════════════════════════════════════════════════════════════════════
# FILTER DATA
# ══════════════════════════════════════════════════════════════════════════════

# File delivery filtering
df_files_filtered = df_files[
    df_files[COL_BRAND].isin(sel_brands)
    & df_files[COL_FILE_NAME].isin(sel_files)
].copy()

if sel_lifecycle != "All":
    df_files_filtered = df_files_filtered[
        df_files_filtered[COL_DELIVERY_LIFECYCLE] == sel_lifecycle
    ].copy()

# Check detail filtering
df_checks_filtered = df_checks[
    df_checks[COL_BRAND].isin(sel_brands)
    & df_checks[COL_CHECK_NAME].isin(sel_checks)
].copy()

# Date range for header
if not df_files_filtered.empty:
    min_date = df_files_filtered[COL_REPORTING_DATE].min()
    max_date = df_files_filtered[COL_REPORTING_DATE].max()
    date_range = (
        f"{min_date.strftime('%d %b')} – {max_date.strftime('%d %b %Y')}"
        if hasattr(min_date, "strftime")
        else f"{min_date} – {max_date}"
    )
else:
    date_range = "No data"


# ══════════════════════════════════════════════════════════════════════════════
# RENDER DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

# Header
render_header(
    title=DASHBOARD_HEADING,
    subtitle=DASHBOARD_SUBTITLE,
    brand_label=brand_label,
    wallet_label="All Files",
    latest_run=latest_run,
    date_range=date_range,
)

# ── Tabs ──────────────────────────────────────────────────────────────────
tab_files, tab_checks = st.tabs(["📁 File Delivery", "🔍 Check Detail"])

# ── Tab 1: File Delivery ─────────────────────────────────────────────────
with tab_files:
    render_file_kpi_section(df_files_filtered)
    render_file_heatmap(
        df_files_filtered,
        status_col=sel_file_status_col,
        status_label=sel_file_status_label,
    )
    render_file_detail_table(df_files_filtered)

# ── Tab 2: Check Detail ──────────────────────────────────────────────────
with tab_checks:
    render_kpi_section(df_checks_filtered)
    render_heatmap(
        df_checks_filtered,
        status_col=sel_check_status_col,
        status_label=sel_check_status_label,
    )
    render_detail_table(df_checks_filtered, view_mode=sel_check_view)
