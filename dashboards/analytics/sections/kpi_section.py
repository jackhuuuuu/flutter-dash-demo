# dashboards/analytics/sections/kpi_section.py
"""
KPI cards section — renders the top-level metric cards.
"""

import streamlit as st
import pandas as pd

from flutter_dash.components import kpi_card, section_title
from flutter_dash.helpers import Comparison, MetricDef
from flutter_dash.data.aggregation import aggregate_metrics
from flutter_dash.formatters import format_comparison

from dashboards.analytics.config import KPI_METRICS, METRIC_DRIVERS


def render_kpi_section(
    df_period: pd.DataFrame,
    period: str,
    brand_label: str,
    product_label: str,
) -> None:
    """
    Render the KPI cards row.

    Parameters
    ----------
    df_period : DataFrame
        Filtered data for the selected period.
    period : str
        Period label (e.g. "MTD").
    brand_label, product_label : str
        Display labels for the active filters.
    """
    section_title("Key Metrics", f"{period} · {brand_label} · {product_label}")

    if df_period.empty:
        st.warning("No data available for the selected period and filters.")
        return

    # Aggregate all KPI metrics
    aggs = aggregate_metrics(df_period, KPI_METRICS)

    # Build KPI cards in columns
    cols = st.columns(len(KPI_METRICS))

    for i, metric_def in enumerate(KPI_METRICS):
        agg = aggs[metric_def.label]

        # Build comparisons (vs LY and vs Budget)
        comparisons = []
        for ref_label, ref_key in [("vs LY", "ly"), ("vs Budget", "bud")]:
            ref_val = agg[ref_key]
            ty_val = agg["ty"]
            delta = ty_val - ref_val

            if metric_def.is_pct:
                # For percentages, delta is in pp, pct is relative
                delta_pct = delta  # already in decimal pp
            else:
                delta_pct = delta / ref_val if ref_val != 0 else 0.0

            comparisons.append(Comparison(
                label=ref_label,
                ref_value=ref_val,
                delta=delta,
                delta_pct=delta_pct,
            ))

        # Resolve drivers for this metric
        driver_cols = METRIC_DRIVERS.get(metric_def.label, [])
        drivers = None
        if driver_cols:
            missing = [c for c in driver_cols if c not in df_period.columns]
            if not missing:
                drivers = {}
                for col in driver_cols:
                    # Pretty-print column name: "volume_effect" → "Volume Effect"
                    label = col.replace("_", " ").title()
                    drivers[label] = df_period[col].sum()

        with cols[i]:
            kpi_card(
                title=metric_def.label,
                value=agg["ty"],
                comparisons=comparisons,
                formatter=metric_def.formatter,
                drivers=drivers,
                flippable=drivers is not None,
                card_index=i,
                period_label=period,
                is_pct=metric_def.is_pct,
            )
