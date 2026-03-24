# flutter_dash/__init__.py
"""
Flutter Dash — Reusable Streamlit dashboard toolkit for finance reporting.

This package provides:
  - Standardised theme system (dark/light palettes, CSS, Plotly layouts)
  - Ready-made UI components (KPI cards, charts, tables, sidebar builder)
  - Data helpers (filters, aggregation, date utilities)
  - Integration stubs for Databricks Unity Catalog and Genie AI

Quick start:
    from flutter_dash import apply_theme, fmt_currency, fmt_pct
    from flutter_dash.components import kpi_card, line_chart, bar_chart
"""

# ── Theme ─────────────────────────────────────────────────────────────────────
from flutter_dash.theme import apply_theme  # noqa: F401

# ── Formatters (re-export for convenience) ────────────────────────────────────
from flutter_dash.formatters import (  # noqa: F401
    fmt_currency,
    fmt_pct,
    fmt_number,
    format_comparison,
)

# ── Helpers (re-export for convenience) ───────────────────────────────────────
from flutter_dash.helpers import (  # noqa: F401
    delta_colour,
    delta_arrow,
    Comparison,
    MetricDef,
    SeriesStyle,
)
