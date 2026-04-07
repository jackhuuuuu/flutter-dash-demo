# sections/heatmap.py
"""
Status heatmap grid — shows PASS/FAIL status per check per date.

This is the most operationally useful view in the dashboard.
It answers "which checks broke on which days?" at a glance.

Layout:
  - X-axis: reporting dates (columns)
  - Y-axis: check names (rows)
  - Colour: green = PASS, red = FAIL
"""

import streamlit as st
import pandas as pd
from typing import List

from flutter_dash.theme import get_active_theme
from flutter_dash.components import section_title, heatmap_chart

from config import (
    COL_REPORTING_DATE, COL_CHECK_NAME,
    COL_OVERALL_STATUS, COL_REVENUE_STATUS, COL_EPM_STATUS,
    STATUS_PASS, STATUS_FAIL, STATUS_TYPES,
)


def render_heatmap(
    df: pd.DataFrame,
    status_col: str = COL_OVERALL_STATUS,
    status_label: str = "Overall",
) -> None:
    """
    Render the status heatmap grid.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    status_col : str
        Which status column to use for colouring (overall, revenue, or epm).
    status_label : str
        Human-readable label for the selected status type.
    """
    section_title(
        "Check Status Grid",
        f"PASS / FAIL by date — {status_label} status",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Build the heatmap matrix ──────────────────────────────────────────
    # Pivot the data: rows = check_name, columns = reporting_date, values = status
    # Convert status to numeric: PASS = 1, FAIL = 0
    df_pivot = df.copy()
    df_pivot["_status_num"] = df_pivot[status_col].map({
        STATUS_PASS: 1,
        STATUS_FAIL: 0,
    })

    # Pivot to a matrix (check_name × reporting_date)
    matrix = df_pivot.pivot_table(
        index=COL_CHECK_NAME,
        columns=COL_REPORTING_DATE,
        values="_status_num",
        aggfunc="min",  # If any check for a date is FAIL, show FAIL
    )

    # Sort dates left-to-right, checks alphabetically
    matrix = matrix.sort_index(axis=1)  # sort columns (dates)
    matrix = matrix.sort_index(axis=0)  # sort rows (check names)

    # Fill NaN with -1 (no data) — these will show as grey
    matrix = matrix.fillna(-1)

    # ── Prepare labels ────────────────────────────────────────────────────
    # Format dates as "dd Mon" for readability
    x_labels = [d.strftime("%d %b") if hasattr(d, "strftime") else str(d)
                for d in matrix.columns]
    y_labels = list(matrix.index)

    # ── Prepare hover text ────────────────────────────────────────────────
    text_values = []
    for check_name in matrix.index:
        row_text = []
        for dt in matrix.columns:
            val = matrix.loc[check_name, dt]
            if val == 1:
                row_text.append("PASS ✓")
            elif val == 0:
                row_text.append("FAIL ✗")
            else:
                row_text.append("—")
        text_values.append(row_text)

    # ── Colourscale: FAIL (red) → no data (grey) → PASS (green) ──────────
    # Map: -1 = no data (0.0), 0 = FAIL (0.5), 1 = PASS (1.0)
    # We normalise: zmin=-1, zmax=1, so -1→0.0, 0→0.5, 1→1.0
    colorscale = [
        [0.0, tokens.bg_elevated],   # no data → grey/elevated
        [0.25, tokens.bg_elevated],  # transition
        [0.40, tokens.negative],     # FAIL → red
        [0.60, tokens.negative],     # FAIL → red
        [0.75, tokens.positive],     # PASS → green
        [1.0, tokens.positive],      # PASS → green
    ]

    # ── Dynamic height: scale with number of checks ──────────────────────
    chart_height = max(300, len(y_labels) * 30 + 100)

    # ── Render ────────────────────────────────────────────────────────────
    fig = heatmap_chart(
        z_values=matrix.values.tolist(),
        x_labels=x_labels,
        y_labels=y_labels,
        text_values=text_values,
        colorscale=colorscale,
        title="",
        height=chart_height,
        zmin=-1,
        zmax=1,
        show_colorbar=False,
        hover_template=(
            "<b>%{y}</b><br>"
            "Date: %{x}<br>"
            "Status: %{text}<extra></extra>"
        ),
    )

    st.plotly_chart(fig, key="status_heatmap")
