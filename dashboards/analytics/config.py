# dashboards/analytics/config.py
"""
Configuration for the Flutter Analytics dashboard.

This file contains all dashboard-specific settings:
  - Page config (title, icon)
  - Metric definitions (what metrics to show and how to format them)
  - Driver mappings (what columns explain each metric's variance)
  - Chart metric picker options

To create a NEW dashboard, copy this file and change the settings.
The flutter_dash package provides the building blocks — this file
tells it what to build.
"""

from flutter_dash.helpers import MetricDef
from flutter_dash.formatters import fmt_currency, fmt_pct

# ── Page settings ─────────────────────────────────────────────────────────────
PAGE_TITLE = "Flutter Analytics"
PAGE_ICON = "📊"
DASHBOARD_HEADING = "Performance Dashboard"
DASHBOARD_SUBTITLE = "Multi-brand | Multi-product | TY vs LY vs Budget"

# ── Metric definitions ────────────────────────────────────────────────────────
# Each MetricDef tells the dashboard:
#   - What to call it in the UI
#   - Which columns hold TY / LY / Budget values
#   - How vto format it (currency, percentage, plain number)
#   - Whether it's a percentage (margin) → uses weighted avg, not sum

NET_REVENUE = MetricDef(
    label="Net Revenue",
    ty_col="total_net_revenue",
    ly_col="total_net_revenue_ly",
    bud_col="total_net_revenue_budget",
    formatter=fmt_currency,
)

STAKES = MetricDef(
    label="Stakes",
    ty_col="total_stakes",
    ly_col="total_stakes_ly",
    bud_col="total_stakes_budget",
    formatter=fmt_currency,
)

WINS = MetricDef(
    label="Wins",
    ty_col="total_wins",
    ly_col="total_wins_ly",
    bud_col="total_wins_budget",
    formatter=fmt_currency,
)

BONUS = MetricDef(
    label="Bonus",
    ty_col="total_bonus",
    ly_col="total_bonus_ly",
    bud_col="total_bonus_budget",
    formatter=fmt_currency,
)

MARGIN = MetricDef(
    label="Margin %",
    ty_col="margin",
    ly_col="margin_ly",
    bud_col="margin_budget",
    formatter=fmt_pct,
    is_pct=True,
    weight_col="total_stakes",
)

# Ordered list of KPI metrics (shown as cards at the top)
KPI_METRICS: list[MetricDef] = [NET_REVENUE, STAKES, WINS, BONUS, MARGIN]

# Metrics available in the chart metric picker (sidebar)
CHART_METRIC_OPTIONS: dict[str, MetricDef] = {
    m.label: m for m in KPI_METRICS
}

# ── Detail table metrics ──────────────────────────────────────────────────────
# These are the metrics shown in the data table.
# The table automatically creates TY, YoY Δ, YoY %, Bud Var, Bud % columns.
TABLE_METRICS: list[MetricDef] = KPI_METRICS

# Table grouping hierarchy
TABLE_GROUP_BY: list[str] = ["brand", "product"]

# ── Driver mappings ───────────────────────────────────────────────────────────
# Maps metric label → list of driver column names in the source data.
# Used for KPI card flip panels and chart driver tooltips.
# If a metric has no drivers, omit it or set to an empty list.
METRIC_DRIVERS: dict[str, list[str]] = {
    "Net Revenue": ["volume_effect", "spend_effect", "margin_effect"],
    # "Stakes":    ["volume_effect", "stake_per_customer_effect"],  # future
    # "Margin %":  ["product_mix_effect", "odds_effect"],           # future
}

# ── Dimension columns ────────────────────────────────────────────────────────
# These define the filterable dimensions in the sidebar.
DIMENSIONS: dict[str, str] = {
    "brand": "Brand",
    "product": "Product",
}

# Date column name in the source data
DATE_COL = "reporting_date"
