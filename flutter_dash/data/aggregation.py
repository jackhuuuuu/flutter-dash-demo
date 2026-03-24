# flutter_dash/data/aggregation.py
"""
Generic metric aggregation utilities.

These functions work with :class:`~flutter_dash.helpers.MetricDef` objects
so you never have to hard-code column names in your aggregation logic.

Key functions
-------------
- **weighted_average** — weighted mean (e.g. margin weighted by stakes).
- **aggregate_metrics** — aggregate a list of MetricDefs over a DataFrame,
  returning a flat dict of ``{label: {ty, ly, bud}}`` values.
- **aggregate_metric_single** — aggregate one MetricDef → ``{ty, ly, bud}``.
- **get_drivers_daily** — daily-level sum for a list of driver columns.

Usage:
    from flutter_dash.data.aggregation import aggregate_metrics, get_drivers_daily
    from flutter_dash.helpers import MetricDef
    from flutter_dash.formatters import fmt_currency

    metrics = [
        MetricDef("Revenue", "nr", "nr_ly", "nr_bud", fmt_currency),
    ]
    result = aggregate_metrics(df, metrics)
    # result["Revenue"] → {"ty": 123456, "ly": 100000, "bud": 110000}
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from flutter_dash.helpers import MetricDef


# ═════════════════════════════════════════════════════════════════════════════
# 1. WEIGHTED AVERAGE
# ═════════════════════════════════════════════════════════════════════════════

def weighted_average(
    df: pd.DataFrame,
    value_col: str,
    weight_col: str,
) -> float:
    """
    Compute a weighted mean of *value_col* using *weight_col* as weights.

    Rows where either column is NaN or where the weight is ≤ 0 are dropped.
    Returns ``0.0`` if no valid rows remain.

    Parameters
    ----------
    df : DataFrame
        Source data.
    value_col : str
        Column containing the values to average (e.g. ``"margin"``).
    weight_col : str
        Column containing the weights (e.g. ``"total_stakes"``).

    Returns
    -------
    float
        The weighted average.

    Example
    -------
    >>> weighted_average(df, "margin", "total_stakes")
    0.1133
    """
    valid = df[[value_col, weight_col]].dropna()
    valid = valid[valid[weight_col] > 0]
    if valid.empty:
        return 0.0
    return (valid[value_col] * valid[weight_col]).sum() / valid[weight_col].sum()


# ═════════════════════════════════════════════════════════════════════════════
# 2. SINGLE-METRIC AGGREGATION
# ═════════════════════════════════════════════════════════════════════════════

def _resolve_weight_col(metric: MetricDef, period: str) -> str | None:
    """
    Resolve the weight column for a given period suffix.

    For ``weight_col="total_stakes"`` and a LY column like
    ``"margin_ly"`` we look for ``"total_stakes_ly"`` in the data.
    If the dataset uses a different convention, callers should create
    a MetricDef with the correct weight_col per period.
    """
    if metric.weight_col is None:
        return None

    # Determine the suffix from the metric column
    base = metric.weight_col  # e.g. "total_stakes"
    if period == "ly":
        return f"{base}_ly"
    elif period == "bud":
        return f"{base}_budget"
    return base  # TY


def aggregate_metric_single(
    df: pd.DataFrame,
    metric: MetricDef,
) -> dict[str, float]:
    """
    Aggregate one MetricDef over a DataFrame.

    Returns
    -------
    dict
        ``{"ty": float, "ly": float, "bud": float}``
        Sum for simple metrics, weighted average for ``is_pct=True``
        metrics that have a ``weight_col``.
    """
    if df.empty:
        return {"ty": 0.0, "ly": 0.0, "bud": 0.0}

    result: dict[str, float] = {}
    for key, col, period in [
        ("ty", metric.ty_col, "ty"),
        ("ly", metric.ly_col, "ly"),
        ("bud", metric.bud_col, "bud"),
    ]:
        if col not in df.columns:
            result[key] = 0.0
            continue

        if metric.weight_col is not None:
            w_col = _resolve_weight_col(metric, period)
            if w_col and w_col in df.columns:
                result[key] = weighted_average(df, col, w_col)
            else:
                result[key] = weighted_average(df, col, metric.weight_col)
        else:
            result[key] = df[col].sum()

    return result


# ═════════════════════════════════════════════════════════════════════════════
# 3. MULTI-METRIC AGGREGATION
# ═════════════════════════════════════════════════════════════════════════════

def aggregate_metrics(
    df: pd.DataFrame,
    metric_defs: list[MetricDef],
) -> dict[str, dict[str, float]]:
    """
    Aggregate every metric in *metric_defs* over *df*.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the period/dimensions of interest.
    metric_defs : list[MetricDef]
        Metrics to aggregate.

    Returns
    -------
    dict[str, dict[str, float]]
        Keyed by ``MetricDef.label``.
        Each value is ``{"ty": ..., "ly": ..., "bud": ...}``.

    Example
    -------
    result = aggregate_metrics(df, [revenue_def, margin_def])
    print(result["Net Revenue"]["ty"])   # → 123456.0
    print(result["Margin %"]["ty"])      # → 0.1133
    """
    if df.empty:
        return {m.label: {"ty": 0.0, "ly": 0.0, "bud": 0.0} for m in metric_defs}

    return {
        m.label: aggregate_metric_single(df, m)
        for m in metric_defs
    }


# ═════════════════════════════════════════════════════════════════════════════
# 4. DAILY DRIVERS
# ═════════════════════════════════════════════════════════════════════════════

def get_drivers_daily(
    df: pd.DataFrame,
    date_col: str,
    driver_cols: list[str],
) -> Optional[pd.DataFrame]:
    """
    Return a daily-aggregated DataFrame of driver columns, or ``None``
    if any driver column is missing from *df*.

    Parameters
    ----------
    df : DataFrame
        Source data (should already be filtered by date/dimensions).
    date_col : str
        Name of the date column to group by.
    driver_cols : list[str]
        Column names for the driver values (e.g.
        ``["volume_effect", "spend_effect", "margin_effect"]``).

    Returns
    -------
    DataFrame or None
        Columns: [date_col] + driver_cols, one row per date.
        ``None`` if *driver_cols* is empty or any column is missing.
    """
    if not driver_cols:
        return None

    missing = [c for c in driver_cols if c not in df.columns]
    if missing:
        return None

    return (
        df.groupby(date_col)[driver_cols]
        .sum()
        .reset_index()
    )


# ═════════════════════════════════════════════════════════════════════════════
# 5. DAILY WEIGHTED AVERAGE (for trend charts of pct metrics)
# ═════════════════════════════════════════════════════════════════════════════

def daily_weighted_average(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    weight_col: str,
) -> pd.DataFrame:
    """
    Compute a weighted average of *value_col* per day.

    Useful for trend charts of percentage metrics like margin, where a
    simple ``groupby().mean()`` would be incorrect — you need to weight
    by the associated volume column (e.g. stakes).

    Parameters
    ----------
    df : DataFrame
        Source data.
    date_col : str
        Date column name.
    value_col : str
        Column to average (e.g. ``"margin"``).
    weight_col : str
        Column to weight by (e.g. ``"total_stakes"``).

    Returns
    -------
    DataFrame
        Two columns: [date_col, value_col], one row per date.
    """
    def _wm(group: pd.DataFrame) -> float:
        w = group[weight_col]
        v = group[value_col]
        total_w = w.sum()
        if total_w > 0:
            return (v * w).sum() / total_w
        return 0.0

    result = (
        df.groupby(date_col)
        .apply(_wm, include_groups=False)
        .reset_index(name=value_col)
    )
    return result
