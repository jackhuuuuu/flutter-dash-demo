# sections/file_heatmap.py
"""
File delivery heatmap — shows delivery timeliness per file per date.

Layout:
  - X-axis: reporting dates
  - Y-axis: file names
  - Colour: green = on time (0d), yellow = D+1 (1d), red = late (>1d),
            grey = no data

Based on erp_delivery_days derived from erp_final_delivered_at.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.components import section_title, heatmap_chart

from config import (
    COL_REPORTING_DATE, COL_FILE_NAME,
    COL_ERP_DELIVERY_DAYS, COL_DELIVERY_LIFECYCLE,
    COL_ERP_FINAL_DELIVERED_AT, COL_LATEST_ROW_COUNT,
)


def render_file_heatmap(
    df: pd.DataFrame,
    status_col: str = "",
    status_label: str = "Overall",
) -> None:
    """
    Render the file delivery timeliness heatmap.

    Colour encodes delivery days: 0 = green, 1 = yellow, >1 = red.
    All detail is in the hover tooltip only — no text on cells.

    Parameters
    ----------
    df : DataFrame
        Filtered file delivery data.
    status_col : str
        Unused — kept for call-signature compatibility. Colour is based
        on erp_delivery_days.
    status_label : str
        Human-readable label for subtitle.
    """
    section_title(
        "File Delivery Grid",
        f"Delivery timeliness by file and date — {status_label}",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Map delivery days to heatmap values ───────────────────────────────
    # 0 days = 2 (green), 1 day = 1 (yellow), >1 day = 0 (red), no data = -1
    df_pivot = df.copy()

    def _day_to_num(days):
        if pd.isna(days):
            return -1
        d = int(days)
        if d <= 0:
            return 2   # on time
        elif d == 1:
            return 1   # acceptable (D+1)
        else:
            return 0   # late

    df_pivot["_day_num"] = df_pivot[COL_ERP_DELIVERY_DAYS].apply(_day_to_num)

    matrix = df_pivot.pivot_table(
        index=COL_FILE_NAME,
        columns=COL_REPORTING_DATE,
        values="_day_num",
        aggfunc="min",  # worst case if duplicates
    )

    matrix = matrix.sort_index(axis=1)
    matrix = matrix.sort_index(axis=0)
    matrix = matrix.fillna(-1)

    x_labels = [d.strftime("%d %b") if hasattr(d, "strftime") else str(d)
                for d in matrix.columns]
    y_labels = list(matrix.index)

    # ── Build hover text (tooltip only — no cell text) ────────────────────
    # Pre-pivot extra columns for tooltip content
    days_pivot = df_pivot.pivot_table(
        index=COL_FILE_NAME, columns=COL_REPORTING_DATE,
        values=COL_ERP_DELIVERY_DAYS, aggfunc="first",
    ).reindex(index=matrix.index, columns=matrix.columns)

    lifecycle_pivot = df_pivot.pivot_table(
        index=COL_FILE_NAME, columns=COL_REPORTING_DATE,
        values=COL_DELIVERY_LIFECYCLE, aggfunc="first",
    ).reindex(index=matrix.index, columns=matrix.columns)

    rows_pivot = df_pivot.pivot_table(
        index=COL_FILE_NAME, columns=COL_REPORTING_DATE,
        values=COL_LATEST_ROW_COUNT, aggfunc="first",
    ).reindex(index=matrix.index, columns=matrix.columns)

    text_values = []
    for fname in matrix.index:
        row_text = []
        for dt in matrix.columns:
            val = matrix.loc[fname, dt]
            if val == -1:
                row_text.append("No data")
            else:
                days = days_pivot.loc[fname, dt]
                days_str = f"{int(days)}d" if pd.notna(days) else "—"
                lc = lifecycle_pivot.loc[fname, dt]
                lc_str = str(lc).replace("_", " ").title() if pd.notna(lc) else "—"
                rc = rows_pivot.loc[fname, dt]
                rc_str = f"{int(rc):,}" if pd.notna(rc) else "—"
                row_text.append(f"Days: {days_str} | {lc_str} | Rows: {rc_str}")
        text_values.append(row_text)

    # ── Colorscale: late(red) → D+1(yellow) → on-time(green) ─────────────
    # z range: -1 (no data) to 2 (on time)
    # Normalised: -1→0.0, 0→0.33, 1→0.67, 2→1.0
    colorscale = [
        [0.0, tokens.bg_elevated],    # no data → grey
        [0.20, tokens.bg_elevated],
        [0.21, tokens.negative],      # late (>1d) → red
        [0.44, tokens.negative],
        [0.45, tokens.warning],       # D+1 (1d) → yellow
        [0.66, tokens.warning],
        [0.67, tokens.positive],      # on time (0d) → green
        [1.0, tokens.positive],
    ]

    chart_height = max(300, len(y_labels) * 35 + 100)

    fig = heatmap_chart(
        z_values=matrix.values.tolist(),
        x_labels=x_labels,
        y_labels=y_labels,
        text_values=text_values,
        colorscale=colorscale,
        title="",
        height=chart_height,
        zmin=-1,
        zmax=2,
        show_colorbar=False,
        show_text=False,
        hover_template=(
            "<b>%{y}</b><br>"
            "Date: %{x}<br>"
            "%{text}<extra></extra>"
        ),
    )

    st.plotly_chart(fig, key="file_delivery_heatmap")
