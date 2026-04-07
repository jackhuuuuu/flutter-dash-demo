# sections/lifecycle_section.py
"""
Failure lifecycle section — shows the breakdown of check failure states.

Renders two donut charts side-by-side:
  - Revenue failure lifecycle (NEVER_FAILED / RESOLVED / UNRESOLVED)
  - EPM failure lifecycle

This gives operators visibility into how many checks have historically
had issues and whether those issues were resolved.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.components import section_title, pie_chart
from flutter_dash.formatters import fmt_number

from config import (
    COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE,
    LIFECYCLE_NEVER_FAILED, LIFECYCLE_RESOLVED, LIFECYCLE_UNRESOLVED,
)


def _lifecycle_summary(df: pd.DataFrame, lifecycle_col: str) -> pd.DataFrame:
    """
    Count checks in each lifecycle state.

    Returns a DataFrame with columns: lifecycle, count
    """
    counts = df[lifecycle_col].value_counts().reset_index()
    counts.columns = ["lifecycle", "count"]

    # Ensure all three states are present (even if count is 0)
    all_states = [LIFECYCLE_NEVER_FAILED, LIFECYCLE_RESOLVED, LIFECYCLE_UNRESOLVED]
    existing = set(counts["lifecycle"])
    for state in all_states:
        if state not in existing:
            counts = pd.concat([
                counts,
                pd.DataFrame({"lifecycle": [state], "count": [0]}),
            ], ignore_index=True)

    # Sort in logical order: NEVER_FAILED → RESOLVED → UNRESOLVED
    order = {LIFECYCLE_NEVER_FAILED: 0, LIFECYCLE_RESOLVED: 1, LIFECYCLE_UNRESOLVED: 2}
    counts["_sort"] = counts["lifecycle"].map(order)
    counts = counts.sort_values("_sort").drop(columns=["_sort"])

    return counts


def render_lifecycle_section(df: pd.DataFrame) -> None:
    """
    Render the failure lifecycle donut charts.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    """
    section_title(
        "Failure Lifecycle",
        "How many checks have ever failed, and whether they were resolved",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Prepare summaries ─────────────────────────────────────────────────
    rev_summary = _lifecycle_summary(df, COL_REV_LIFECYCLE)
    epm_summary = _lifecycle_summary(df, COL_EPM_LIFECYCLE)

    # ── Render side-by-side donut charts ──────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        fig_rev = pie_chart(
            df=rev_summary,
            label_col="lifecycle",
            value_col="count",
            formatter=fmt_number,
            title="Revenue Lifecycle",
            height=350,
            hole=0.5,
        )
        # Override colours: green for never_failed, accent for resolved, red for unresolved
        fig_rev.update_traces(
            marker=dict(colors=[
                tokens.positive,   # NEVER_FAILED
                tokens.accent,     # RESOLVED
                tokens.negative,   # UNRESOLVED
            ]),
        )
        st.plotly_chart(fig_rev, key="lifecycle_revenue")

    with col_right:
        fig_epm = pie_chart(
            df=epm_summary,
            label_col="lifecycle",
            value_col="count",
            formatter=fmt_number,
            title="EPM Lifecycle",
            height=350,
            hole=0.5,
        )
        fig_epm.update_traces(
            marker=dict(colors=[
                tokens.positive,
                tokens.accent,
                tokens.negative,
            ]),
        )
        st.plotly_chart(fig_epm, key="lifecycle_epm")
