# sections/trend_section.py
"""
Daily trend section — shows pass/fail counts over time.

Renders a stacked bar chart with the number of PASS and FAIL checks
per reporting date, giving an at-a-glance view of data quality health
over the trailing 31 days.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.components import section_title, bar_chart
from flutter_dash.helpers import SeriesStyle
from flutter_dash.formatters import fmt_number

from config import COL_REPORTING_DATE, COL_OVERALL_STATUS, STATUS_PASS, STATUS_FAIL


def render_trend_section(
    df: pd.DataFrame,
    status_col: str = COL_OVERALL_STATUS,
    status_label: str = "Overall",
) -> None:
    """
    Render the daily pass/fail trend as a stacked bar chart.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    status_col : str
        Which status column to aggregate (overall, revenue, or epm).
    status_label : str
        Human-readable label for the subtitle.
    """
    section_title(
        "Daily Trend",
        f"Pass vs Fail count by date — {status_label} status",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Aggregate: count PASS and FAIL per date ──────────────────────────
    daily = df.groupby(COL_REPORTING_DATE).apply(
        lambda g: pd.Series({
            "pass_count": (g[status_col] == STATUS_PASS).sum(),
            "fail_count": (g[status_col] == STATUS_FAIL).sum(),
        })
    ).reset_index()

    # Sort by date
    daily = daily.sort_values(COL_REPORTING_DATE)

    # Format date column for display
    daily["date_label"] = daily[COL_REPORTING_DATE].apply(
        lambda d: d.strftime("%d %b") if hasattr(d, "strftime") else str(d)
    )

    # ── Chart styles ──────────────────────────────────────────────────────
    styles = [
        SeriesStyle(label="Pass", colour=tokens.positive, dash="solid"),
        SeriesStyle(label="Fail", colour=tokens.negative, dash="solid"),
    ]

    # ── Render stacked bar chart ──────────────────────────────────────────
    fig = bar_chart(
        df=daily,
        x_col="date_label",
        y_cols=["pass_count", "fail_count"],
        series_styles=styles,
        formatter=fmt_number,
        title="",
        height=380,
        barmode="stack",
    )

    # Show values inside bars instead of outside to avoid overlap on stacks.
    # Override text colour to white so numbers are readable against the
    # coloured bar backgrounds (the bar_chart component defaults to using
    # the series colour for text, which is invisible on a same-colour bar).
    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=11),
    )

    st.plotly_chart(fig, key="daily_trend")
