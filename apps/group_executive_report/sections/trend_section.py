# sections/trend_section.py
"""
Daily trend line chart section.
"""

import streamlit as st
import pandas as pd
from datetime import timedelta

from flutter_dash.components import line_chart, section_title
from flutter_dash.helpers import MetricDef, SeriesStyle
from flutter_dash.data.aggregation import daily_weighted_average, get_drivers_daily
from flutter_dash.data.filters import filter_df

from config import DATE_COL, METRIC_DRIVERS


def render_trend_section(
    df_raw: pd.DataFrame,
    max_date,
    metric_def: MetricDef,
    brand_label: str,
    product_label: str,
    dimension_filters: dict,
) -> None:
    """
    Render the daily trend line chart (last 30 days).

    Parameters
    ----------
    df_raw : DataFrame
        Unfiltered raw data (will be filtered to last 30 days).
    max_date : date
        Latest date in the dataset.
    metric_def : MetricDef
        The selected chart metric.
    brand_label, product_label : str
        Display labels for active filters.
    dimension_filters : dict
        Dimension filters to apply (e.g. ``{"brand": [...], "product": [...]}``)
    """
    section_title(
        f"Daily Trend — {metric_def.label}",
        f"Last 30 days · {brand_label} · {product_label} · TY vs LY vs Budget",
    )

    # Filter to last 30 days
    last30_start = max_date - timedelta(days=29)
    df_line = filter_df(
        df_raw, DATE_COL, last30_start, max_date, **dimension_filters
    )

    if df_line.empty:
        st.info("No data available for the last 30 days with the current filters.")
        return

    # Build daily aggregation
    y_cols = [metric_def.ty_col, metric_def.ly_col, metric_def.bud_col]

    if metric_def.is_pct and metric_def.weight_col:
        # Weighted average per day (e.g. margin weighted by stakes)
        dates = sorted(df_line[DATE_COL].unique())
        line_daily = pd.DataFrame({DATE_COL: dates})

        weight_cols = {
            metric_def.ty_col: metric_def.weight_col,
            metric_def.ly_col: f"{metric_def.weight_col}_ly",
            metric_def.bud_col: f"{metric_def.weight_col}_budget",
        }

        for val_col, w_col in weight_cols.items():
            if w_col not in df_line.columns:
                w_col = metric_def.weight_col  # fallback
            dwa = daily_weighted_average(df_line, DATE_COL, val_col, w_col)
            line_daily = line_daily.merge(dwa, on=DATE_COL, how="left")
    else:
        # Simple sum per day
        line_daily = (
            df_line
            .groupby(DATE_COL)[y_cols]
            .sum()
            .reset_index()
            .sort_values(DATE_COL)
        )

    line_daily[DATE_COL] = pd.to_datetime(line_daily[DATE_COL])

    # Series styles: TY, LY, Budget — standardised colours
    styles = [
        SeriesStyle(label="TY",     colour="#00D4FF", dash="solid"),
        SeriesStyle(label="LY",     colour="#7AB7E2", dash="dash"),
        SeriesStyle(label="Budget", colour="#FFB300", dash="dot"),
    ]

    # Resolve drivers for the chart tooltips
    driver_cols = METRIC_DRIVERS.get(metric_def.label, [])
    drivers_daily = get_drivers_daily(df_line, DATE_COL, driver_cols)

    fig = line_chart(
        df=line_daily,
        x_col=DATE_COL,
        y_cols=y_cols,
        series_styles=styles,
        formatter=metric_def.formatter,
        title=f"Daily {metric_def.label} — Last 30 Days",
        drivers_df=drivers_daily,
        drivers_formatter=None,
    )
    st.plotly_chart(fig, width="stretch")
