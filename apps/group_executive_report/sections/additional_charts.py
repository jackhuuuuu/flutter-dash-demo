# sections/additional_charts.py
"""
Additional chart examples — pie and waterfall charts.

The pie chart reflects the selected primary metric and uses the
sidebar "Chart Grouping" dropdown for its dimension. The waterfall
shows a Net Revenue LY-to-TY bridge.
"""

import streamlit as st
import pandas as pd

from flutter_dash.components import pie_chart, waterfall_chart, section_title, multi_section_title
from flutter_dash.formatters import fmt_currency
from flutter_dash.helpers import MetricDef
from flutter_dash.data.aggregation import weighted_average

from config import METRIC_DRIVERS


def render_additional_charts(
    df_period: pd.DataFrame,
    metric_def: MetricDef,
    period: str,
    brand_label: str,
    product_label: str,
    grouping: str = "product",
) -> None:
    """
    Render additional chart examples beneath the main dashboard sections.

    Includes:
      1. Metric composition donut chart (grouped by sidebar selection)
      2. Net Revenue Bridge — LY to TY (waterfall chart)

    The pie chart respects the primary metric selection from the sidebar.
    For percentage metrics (e.g. Margin %), it shows a weighted-average
    breakdown instead of a sum-based composition.

    Parameters
    ----------
    df_period : DataFrame
        Filtered data for the selected period.
    metric_def : MetricDef
        The selected chart metric.
    period, brand_label, product_label : str
        Display labels.
    grouping : str
        Dimension column to group by ("brand" or "product").
    """
    if df_period.empty:
        return

    dim = grouping
    dim_label = dim.title()
    is_pct_metric = metric_def.is_pct

    # ── Section titles — one per chart, matching column layout ────────────────
    if is_pct_metric:
        pie_title_text = f"{metric_def.label} by {dim_label}"
        pie_subtitle = (
            f"{period} · {brand_label} · {product_label} · "
            f"Weighted average {metric_def.label.lower()}"
        )
    else:
        pie_title_text = f"{metric_def.label} Mix by {dim_label}"
        pie_subtitle = (
            f"{period} · {brand_label} · {product_label} · "
            f"TY {metric_def.label} composition"
        )

    multi_section_title(
        [
            (pie_title_text, pie_subtitle),
            ("Net Revenue Bridge", f"{period} · LY to TY variance drivers"),
        ],
        col_ratios=[3, 2],
    )

    # ── 1. Metric Composition Donut ───────────────────────────────────────────
    col1, col2 = st.columns([3, 2])
    with col1:
        if is_pct_metric and metric_def.weight_col:
            # For percentage metrics, show weighted average per group
            groups = sorted(df_period[dim].unique())
            rows = []
            for grp in groups:
                grp_df = df_period[df_period[dim] == grp]
                w_avg = weighted_average(
                    grp_df, metric_def.ty_col, metric_def.weight_col,
                )
                rows.append({dim: grp, metric_def.ty_col: w_avg})
            pie_data = pd.DataFrame(rows).sort_values(
                metric_def.ty_col, ascending=False,
            )
            chart_title = f"{metric_def.label} by {dim_label} ({period})"
        else:
            # Sum-based composition for absolute metrics
            pie_data = (
                df_period
                .groupby(dim)[metric_def.ty_col]
                .sum()
                .reset_index()
                .sort_values(metric_def.ty_col, ascending=False)
            )
            chart_title = f"{metric_def.label} Share by {dim_label} ({period})"

        fig_pie = pie_chart(
            df=pie_data,
            label_col=dim,
            value_col=metric_def.ty_col,
            formatter=metric_def.formatter,
            title=chart_title,
            height=400,
            hole=0.45,
        )
        st.plotly_chart(fig_pie, width="stretch")

    # ── 2. Revenue Bridge (Waterfall) ─────────────────────────────────────────
    with col2:
        # Build bridge: LY Total → driver effects → TY Total
        ly_total = df_period["total_net_revenue_ly"].sum()
        ty_total = df_period["total_net_revenue"].sum()

        driver_cols = METRIC_DRIVERS.get("Net Revenue", [])
        categories = ["LY Revenue"]
        values = [ly_total]

        for d_col in driver_cols:
            if d_col in df_period.columns:
                d_label = d_col.replace("_", " ").title()
                d_val = df_period[d_col].sum()
                categories.append(d_label)
                values.append(d_val)

        categories.append("TY Revenue")
        values.append(ty_total)

        fig_wf = waterfall_chart(
            categories=categories,
            values=values,
            formatter=fmt_currency,
            title=f"Net Revenue Bridge — LY to TY ({period})",
            height=400,
        )
        st.plotly_chart(fig_wf, width="stretch")
