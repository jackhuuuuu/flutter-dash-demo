# sections/heatmap.py
"""
Status heatmap grid — shows PASS/FAIL status per check per date.

This is the most operationally useful view in the dashboard.
It answers "which checks broke on which days?" at a glance.

Layout:
  - X-axis: reporting dates (columns)
  - Y-axis: check names (rows)
  - Colour: green = PASS, red = FAIL
  - Tooltip: check values and tolerances for quick diagnosis
"""

import streamlit as st
import pandas as pd
from typing import List

from flutter_dash.theme import get_active_theme
from flutter_dash.components import section_title, heatmap_chart

from config import (
    COL_REPORTING_DATE, COL_CHECK_NAME,
    COL_OVERALL_STATUS, COL_REVENUE_STATUS, COL_EPM_STATUS,
    COL_CHECK_DAILY_VALUE, COL_CHECK_MTD_VALUE,
    COL_DAILY_REV_TOLERANCE, COL_MTD_REV_TOLERANCE,
    COL_DAILY_EPM_TOLERANCE, COL_MTD_EPM_TOLERANCE,
    STATUS_PASS, STATUS_FAIL,
)


def _fmt_val(val) -> str:
    """Format a numeric value for tooltip."""
    if pd.isna(val):
        return "—"
    return f"{float(val):,.4f}"


def _fmt_tol(val) -> str:
    """Format a tolerance value (-1 means N/A)."""
    if pd.isna(val):
        return "N/A"
    v = float(val)
    if v == -1:
        return "N/A"
    return f"{v:,.0f}"


def render_heatmap(df: pd.DataFrame) -> None:
    """
    Render the status heatmap grid.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    """
    section_title(
        "Check Status Grid",
        "PASS / FAIL by date — hover for check values & tolerances",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Build the heatmap matrix ──────────────────────────────────────────
    df_pivot = df.copy()
    df_pivot["_status_num"] = df_pivot[COL_OVERALL_STATUS].map({
        STATUS_PASS: 1,
        STATUS_FAIL: 0,
    })

    matrix = df_pivot.pivot_table(
        index=COL_CHECK_NAME,
        columns=COL_REPORTING_DATE,
        values="_status_num",
        aggfunc="min",
    )

    matrix = matrix.sort_index(axis=1)
    matrix = matrix.sort_index(axis=0)
    matrix = matrix.fillna(-1)

    x_labels = [d.strftime("%d %b") if hasattr(d, "strftime") else str(d)
                for d in matrix.columns]
    y_labels = list(matrix.index)

    # ── Pivot extra columns for tooltip ───────────────────────────────────
    def _pivot_col(col):
        return df_pivot.pivot_table(
            index=COL_CHECK_NAME, columns=COL_REPORTING_DATE,
            values=col, aggfunc="first",
        ).reindex(index=matrix.index, columns=matrix.columns)

    daily_val_p = _pivot_col(COL_CHECK_DAILY_VALUE)
    mtd_val_p = _pivot_col(COL_CHECK_MTD_VALUE)
    d_rev_tol_p = _pivot_col(COL_DAILY_REV_TOLERANCE)
    m_rev_tol_p = _pivot_col(COL_MTD_REV_TOLERANCE)
    d_epm_tol_p = _pivot_col(COL_DAILY_EPM_TOLERANCE)
    m_epm_tol_p = _pivot_col(COL_MTD_EPM_TOLERANCE)
    rev_status_p = _pivot_col(COL_REVENUE_STATUS)
    epm_status_p = _pivot_col(COL_EPM_STATUS)

    # ── Build rich hover text ─────────────────────────────────────────────
    text_values = []
    for check_name in matrix.index:
        row_text = []
        for dt in matrix.columns:
            val = matrix.loc[check_name, dt]
            if val == -1:
                row_text.append("No data")
            else:
                status = "PASS" if val == 1 else "FAIL"
                rev_s = rev_status_p.loc[check_name, dt]
                epm_s = epm_status_p.loc[check_name, dt]
                rev_s = str(rev_s) if pd.notna(rev_s) else "—"
                epm_s = str(epm_s) if pd.notna(epm_s) else "—"

                dv = _fmt_val(daily_val_p.loc[check_name, dt])
                mv = _fmt_val(mtd_val_p.loc[check_name, dt])
                drt = _fmt_tol(d_rev_tol_p.loc[check_name, dt])
                mrt = _fmt_tol(m_rev_tol_p.loc[check_name, dt])
                det = _fmt_tol(d_epm_tol_p.loc[check_name, dt])
                met = _fmt_tol(m_epm_tol_p.loc[check_name, dt])

                tooltip = (
                    f"Status: {status} (Rev: {rev_s} | EPM: {epm_s})"
                    f"<br>─────────────────"
                    f"<br>Daily Value: {dv}"
                    f"<br>MTD Value:   {mv}"
                    f"<br>─────────────────"
                    f"<br>ERP Tol:  Daily {drt} | MTD {mrt}"
                    f"<br>EPM Tol:  Daily {det} | MTD {met}"
                )
                row_text.append(tooltip)
        text_values.append(row_text)

    # ── Colourscale: FAIL (red) → no data (grey) → PASS (green) ──────────
    colorscale = [
        [0.0, tokens.bg_elevated],
        [0.25, tokens.bg_elevated],
        [0.40, tokens.negative],
        [0.60, tokens.negative],
        [0.75, tokens.positive],
        [1.0, tokens.positive],
    ]

    chart_height = max(300, len(y_labels) * 30 + 100)

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
        show_text=False,
        hover_template=(
            "<b>%{y}</b><br>"
            "Date: %{x}<br>"
            "%{text}<extra></extra>"
        ),
    )

    st.plotly_chart(fig, key="status_heatmap")
