# flutter_dash/helpers.py
"""
Shared helpers and data structures used across the package.

This module provides:
  1. Colour/arrow utilities for variance display (green ▲ / red ▼)
  2. Dataclasses that define reusable "shapes" of data:
     - Comparison  — represents a variance row (vs LY, vs Budget, etc.)
     - MetricDef   — describes a metric and its columns in the data
     - SeriesStyle — describes how a chart series should look

Think of dataclasses as "named containers" — like a row in a spreadsheet
with named columns, but in Python code.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from flutter_dash.theme.tokens import ThemeTokens


# ═════════════════════════════════════════════════════════════════════════════
# 1. COLOUR & ARROW UTILITIES
# ═════════════════════════════════════════════════════════════════════════════

def delta_colour(val: float, tokens: ThemeTokens) -> str:
    """
    Return the appropriate colour for a variance value.

    Finance convention:
      positive delta → green (favourable)
      negative delta → red (adverse)
      zero           → grey (neutral)

    Parameters
    ----------
    val : float
        The variance/delta value.
    tokens : ThemeTokens
        Active theme (provides the actual colour hex codes).
    """
    if val > 0:
        return tokens.positive
    if val < 0:
        return tokens.negative
    return tokens.neutral


def delta_arrow(val: float) -> str:
    """
    Return ▲ for positive/zero values, ▼ for negative.

    Used next to variance numbers in KPI cards and tables.
    """
    return "▲" if val >= 0 else "▼"


# ═════════════════════════════════════════════════════════════════════════════
# 2. DATACLASSES — reusable data shapes
# ═════════════════════════════════════════════════════════════════════════════


@dataclass
class Comparison:
    """
    A single variance comparison row (e.g. "vs LY" or "vs Budget").

    Used by KPI cards and tables to show how a value compares to a reference.

    Fields
    ------
    label : str
        Display label, e.g. "vs LY", "vs Budget", "vs Forecast"
    ref_value : float
        The reference value to compare against.
    delta : float
        Absolute difference (TY - reference).
    delta_pct : float
        Relative difference as a decimal (e.g. 0.12 = 12%).

    Example
    -------
    comp = Comparison(label="vs LY", ref_value=100_000, delta=12_000, delta_pct=0.12)
    """
    label: str
    ref_value: float
    delta: float
    delta_pct: float


@dataclass
class MetricDef:
    """
    Defines a metric and maps it to columns in the dataset.

    This is how you tell the dashboard "I have a metric called Net Revenue,
    its TY column is 'total_net_revenue', its LY column is '...', and it
    should be formatted as currency."

    Fields
    ------
    label : str
        Human-readable name shown in the UI, e.g. "Net Revenue"
    ty_col : str
        Column name for This Year's value in the DataFrame.
    ly_col : str
        Column name for Last Year's value.
    bud_col : str
        Column name for Budget value.
    formatter : Callable
        Function to format this metric's values (e.g. fmt_currency, fmt_pct).
    is_pct : bool
        True for percentage metrics like Margin (deltas shown in pp).
    weight_col : str, optional
        For weighted-average metrics (like margin), the column to weight by.
        E.g. margin is weighted by stakes.  Leave None for simple sum metrics.

    Example
    -------
    from flutter_dash.formatters import fmt_currency, fmt_pct

    revenue = MetricDef(
        label="Net Revenue",
        ty_col="total_net_revenue",
        ly_col="total_net_revenue_ly",
        bud_col="total_net_revenue_budget",
        formatter=fmt_currency,
    )
    margin = MetricDef(
        label="Margin %",
        ty_col="margin",
        ly_col="margin_ly",
        bud_col="margin_budget",
        formatter=fmt_pct,
        is_pct=True,
        weight_col="total_stakes",
    )
    """
    label: str
    ty_col: str
    ly_col: str
    bud_col: str
    formatter: Callable[[float], str]
    is_pct: bool = False
    weight_col: Optional[str] = None


@dataclass
class SeriesStyle:
    """
    Visual style for one series in a chart.

    Used by line_chart and bar_chart to control how each series looks.

    Fields
    ------
    label : str
        Legend label, e.g. "TY", "LY", "Budget"
    colour : str
        Hex colour code, e.g. "#00D4FF"
    dash : str
        Line dash style: "solid", "dash", or "dot".
        Only used by line charts; ignored by bar charts.

    Example
    -------
    styles = [
        SeriesStyle(label="TY",     colour="#00D4FF", dash="solid"),
        SeriesStyle(label="LY",     colour="#7A8BA8", dash="dash"),
        SeriesStyle(label="Budget", colour="#FFB300", dash="dot"),
    ]
    """
    label: str
    colour: str = ""
    dash: str = "solid"
