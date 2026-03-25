# dashboards/analytics/sections/brand_breakdown.py
"""
Grouped bar chart section — metric breakdown by brand.
"""

import streamlit as st
import pandas as pd

from flutter_dash.components import bar_chart, section_title
from flutter_dash.helpers import MetricDef, SeriesStyle
from flutter_dash.data.aggregation import weighted_average


def render_brand_breakdown(
    df_period: pd.DataFrame,
    metric_def: MetricDef,
    period: str,
    brand_label: str,
    product_label: str,
) -> None:
    """
    Render a grouped bar chart showing the selected metric by brand.

    Parameters
    ----------
    df_period : DataFrame
        Filtered data for the selected period.
    metric_def : MetricDef
        The selected chart metric.
    period, brand_label, product_label : str
        Display labels.
    """
    section_title(
        f"Brand Breakdown — {metric_def.label}",
        f"{period} · {brand_label} · {product_label} · LY vs TY vs Budget",
    )

    if df_period.empty:
        st.info("No data available for the selected period and filters.")
        return

    y_cols = [metric_def.ty_col, metric_def.ly_col, metric_def.bud_col]

    if metric_def.is_pct and metric_def.weight_col:
        # Weighted average per brand
        brands = sorted(df_period["brand"].unique())
        rows = []
        for brand in brands:
            brand_df = df_period[df_period["brand"] == brand]
            row = {"brand": brand}

            weight_cols = {
                metric_def.ty_col: metric_def.weight_col,
                metric_def.ly_col: f"{metric_def.weight_col}_ly",
                metric_def.bud_col: f"{metric_def.weight_col}_budget",
            }

            for val_col, w_col in weight_cols.items():
                if w_col not in brand_df.columns:
                    w_col = metric_def.weight_col
                row[val_col] = weighted_average(brand_df, val_col, w_col)

            rows.append(row)
        bar_agg = pd.DataFrame(rows)
    else:
        # Simple sum per brand
        bar_agg = (
            df_period
            .groupby("brand")[y_cols]
            .sum()
            .reset_index()
        )

    # Series styles match y_cols order: TY, LY, Budget
    # display_order controls bar position: LY(0) | TY(1) | Budget(2)
    styles = [
        SeriesStyle(label="TY",     colour="#00D4FF", display_order=1),
        SeriesStyle(label="LY",     colour="#7AB7E2", display_order=0),
        SeriesStyle(label="Budget", colour="#FFB300", display_order=2),
    ]

    fig = bar_chart(
        df=bar_agg,
        x_col="brand",
        y_cols=y_cols,
        series_styles=styles,
        formatter=metric_def.formatter,
        title=f"{metric_def.label} by Brand ({period})",
        barmode="group",
    )
    st.plotly_chart(fig, width="stretch")
