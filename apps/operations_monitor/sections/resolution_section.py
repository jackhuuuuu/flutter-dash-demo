# sections/resolution_section.py
"""
Resolution time section — shows how long failures take to resolve.

Renders a horizontal bar chart with check names on the y-axis and
resolution time (in hours) on the x-axis, helping identify which
checks are slowest to fix.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.plotly import base_layout
from flutter_dash.components import section_title

from config import (
    COL_CHECK_NAME,
    COL_REV_RESOLUTION_MINS, COL_EPM_RESOLUTION_MINS,
    COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE,
    LIFECYCLE_RESOLVED,
)


def render_resolution_section(df: pd.DataFrame) -> None:
    """
    Render the resolution time bar chart.

    Shows average resolution time per check name for checks that
    have been resolved at least once.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    """
    section_title(
        "Resolution Times",
        "Average time to resolve failures (hours), by check",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Collect resolution times ──────────────────────────────────────────
    # Combine revenue and EPM resolution data into one view
    records = []

    # Revenue resolutions
    rev_resolved = df[df[COL_REV_LIFECYCLE] == LIFECYCLE_RESOLVED].copy()
    if not rev_resolved.empty:
        for _, row in rev_resolved.iterrows():
            mins = row[COL_REV_RESOLUTION_MINS]
            if pd.notna(mins):
                records.append({
                    "check_name": row[COL_CHECK_NAME],
                    "type": "Revenue",
                    "hours": mins / 60,
                })

    # EPM resolutions
    epm_resolved = df[df[COL_EPM_LIFECYCLE] == LIFECYCLE_RESOLVED].copy()
    if not epm_resolved.empty:
        for _, row in epm_resolved.iterrows():
            mins = row[COL_EPM_RESOLUTION_MINS]
            if pd.notna(mins):
                records.append({
                    "check_name": row[COL_CHECK_NAME],
                    "type": "EPM",
                    "hours": mins / 60,
                })

    if not records:
        st.info("No resolved failures to display resolution times for.")
        return

    res_df = pd.DataFrame(records)

    # ── Average resolution hours per check ────────────────────────────────
    avg_by_check = (
        res_df.groupby("check_name")["hours"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )

    # ── Build horizontal bar chart ────────────────────────────────────────
    layout = base_layout(tokens, height=max(300, len(avg_by_check) * 40 + 100))
    layout["margin"]["l"] = 220

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=avg_by_check["hours"],
        y=avg_by_check["check_name"],
        orientation="h",
        marker=dict(color=tokens.accent, opacity=0.85),
        text=[f"{h:.1f}h" for h in avg_by_check["hours"]],
        textposition="outside",
        textfont=dict(size=11, color=tokens.accent, family=tokens.font_mono),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg resolution: %{text}<extra></extra>"
        ),
    ))

    layout["xaxis"]["title"] = dict(
        text="Hours",
        font=dict(size=11, color=tokens.text_muted),
    )
    layout["yaxis"]["autorange"] = True
    layout["showlegend"] = False

    fig.update_layout(**layout)
    st.plotly_chart(fig, key="resolution_times")
