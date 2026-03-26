# app.py
"""
Group Executive Report — Flutter UK&I
Multi-brand | Multi-product | TY vs LY vs Budget

This is the main orchestrator for the Group Executive Report dashboard.
It uses:
  - flutter_dash package for theme, components, data utilities
  - config.py for this dashboard's settings
  - sections/ for each dashboard section

Run locally:
    cd apps/group_executive_report
    streamlit run app.py --server.port 8502

In production, this is deployed as its own Databricks App.
"""

import streamlit as st

from flutter_dash.theme import apply_theme
from flutter_dash.theme.palettes import FLUTTER_DARK, FLUTTER_LIGHT
from flutter_dash.components.sidebar import SidebarBuilder
from flutter_dash.data.filters import filter_df, filter_label

from config import (
    PAGE_TITLE, PAGE_ICON, DASHBOARD_HEADING,
    DATE_COL, DIMENSIONS, CHART_METRIC_OPTIONS,
)
from data_loader import load_data
from sections import (
    render_header,
    render_kpi_section,
    render_trend_section,
    render_brand_breakdown,
    render_detail_table,
    render_additional_charts,
)

# ── Theme ─────────────────────────────────────────────────────────────────────
# Read theme from URL query param (passed from FBI Hub) or default to light.
# Once in session_state, user can toggle independently via sidebar button.
if "theme" not in st.session_state:
    theme_param = st.query_params.get("theme", "light")
    st.session_state.theme = theme_param if theme_param in ("light", "dark") else "light"

_palette = FLUTTER_LIGHT if st.session_state.theme == "light" else FLUTTER_DARK
apply_theme(st, _palette, page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# ── Load Data ─────────────────────────────────────────────────────────────────
df_raw = load_data()
max_date = max(df_raw[DATE_COL])

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar = SidebarBuilder(st)
sidebar.add_header(PAGE_TITLE, DASHBOARD_HEADING)
sidebar.add_theme_toggle()
sidebar.add_period_picker(
    options=["Yesterday", "WTD", "MTD"],
    default_index=2,
    max_date=max_date,
)
sidebar.add_divider()

# Add dimension filters dynamically from config
all_values = {}
for col, label in DIMENSIONS.items():
    values = sorted(df_raw[col].unique())
    all_values[label] = values
    sidebar.add_multiselect(label, values, placeholder=f"All {label}s")

sidebar.add_metric_picker(list(CHART_METRIC_OPTIONS.keys()))
sidebar.add_divider()
sidebar.add_footer(f"Data as of {max_date}")

selections = sidebar.render()

# ── Extract selections ────────────────────────────────────────────────────────
period = selections["period"]
period_start = selections["period_start"]
period_end = selections["period_end"]
sel_metric_label = selections["metric"]
sel_metric = CHART_METRIC_OPTIONS[sel_metric_label]

# Build dimension filter kwargs and labels
dim_filters = {}
dim_labels = {}
for col, label in DIMENSIONS.items():
    sel = selections[label]
    dim_filters[col] = sel
    dim_labels[label] = filter_label(sel, all_values[label], f"{label}s")

brand_label = dim_labels.get("Brand", "All Brands")
product_label = dim_labels.get("Product", "All Products")

# ── Filter data ───────────────────────────────────────────────────────────────
df_period = filter_df(df_raw, DATE_COL, period_start, period_end, **dim_filters)

# ── Render sections ───────────────────────────────────────────────────────────
render_header(
    DASHBOARD_HEADING, brand_label, product_label,
    period, period_start, period_end, max_date,
)

render_kpi_section(df_period, period, brand_label, product_label)

render_trend_section(
    df_raw, max_date, sel_metric,
    brand_label, product_label, dim_filters,
)

render_brand_breakdown(df_period, sel_metric, period, brand_label, product_label)

render_detail_table(df_period, period, brand_label, product_label)

render_additional_charts(df_period, period, brand_label, product_label)
