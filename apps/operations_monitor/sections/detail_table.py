# sections/detail_table.py
"""
Check-level detail table — shows all DQ check results with values & tolerances.

For active failures, shows an action-required view. Otherwise shows
the full check table with check values and tolerance info in tooltips.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import hex_to_rgba
from flutter_dash.components import section_title

from config import (
    COL_REPORTING_DATE, COL_BRAND, COL_WALLET_TYPE, COL_CHECK_NAME,
    COL_REVENUE_STATUS, COL_EPM_STATUS, COL_OVERALL_STATUS,
    COL_CHECK_DAILY_VALUE, COL_CHECK_MTD_VALUE,
    COL_DAILY_REV_TOLERANCE, COL_MTD_REV_TOLERANCE,
    COL_DAILY_EPM_TOLERANCE, COL_MTD_EPM_TOLERANCE,
    COL_REV_FIRST_FAILED, COL_EPM_FIRST_FAILED,
    COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE,
    COL_REV_RESOLUTION_HRS, COL_EPM_RESOLUTION_HRS,
    STATUS_FAIL, LIFECYCLE_UNRESOLVED,
)


def _status_badge(status: str, tokens) -> str:
    """Return an HTML badge for PASS/FAIL status."""
    if status == STATUS_FAIL:
        bg = hex_to_rgba(tokens.negative, 0.15)
        colour = tokens.negative
        icon = "✗"
    else:
        bg = hex_to_rgba(tokens.positive, 0.15)
        colour = tokens.positive
        icon = "✓"
    return (
        f'<span style="background:{bg};color:{colour};padding:2px 8px;'
        f'border-radius:4px;font-size:11px;font-weight:600;">'
        f'{icon} {status}</span>'
    )


def _lifecycle_badge(lifecycle: str, tokens) -> str:
    """Return an HTML badge for lifecycle state."""
    colour_map = {
        LIFECYCLE_UNRESOLVED: tokens.negative,
        "RESOLVED": tokens.positive,
        "NEVER_FAILED": tokens.text_muted,
    }
    colour = colour_map.get(lifecycle, tokens.text_muted)
    bg = hex_to_rgba(colour, 0.12)
    return (
        f'<span style="background:{bg};color:{colour};padding:2px 8px;'
        f'border-radius:4px;font-size:11px;font-weight:600;">'
        f'{lifecycle}</span>'
    )


def _fmt_val(val) -> str:
    """Format a numeric value for display."""
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


def render_detail_table(df: pd.DataFrame, view_mode: str = "Failed Only") -> None:
    """
    Render the check-level detail table.

    Parameters
    ----------
    df : DataFrame
        Filtered check-level DQ monitor data.
    view_mode : str
        "All" shows everything, "Failed Only" shows only failures,
        "Passed Only" shows only passing checks.
    """
    subtitle_map = {
        "All": "Full check results (hover check name for values & tolerances)",
        "Failed Only": "Checks currently failing or unresolved",
        "Passed Only": "Checks currently passing",
    }
    section_title(
        "Check Detail",
        subtitle_map.get(view_mode, subtitle_map["All"]),
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # Filter based on view mode
    if view_mode == "Failed Only":
        display = df[
            (df[COL_OVERALL_STATUS] == STATUS_FAIL)
            | (df[COL_REV_LIFECYCLE] == LIFECYCLE_UNRESOLVED)
            | (df[COL_EPM_LIFECYCLE] == LIFECYCLE_UNRESOLVED)
        ].copy()
    elif view_mode == "Passed Only":
        display = df[df[COL_OVERALL_STATUS] != STATUS_FAIL].copy()
    else:
        display = df.copy()

    if display.empty:
        if view_mode == "Failed Only":
            st.success("🎉 All checks are passing — no action required!")
        else:
            st.info("No matching checks.")
        return

    col_config = [
        (COL_REPORTING_DATE, "Date"),
        (COL_BRAND, "Brand"),
        (COL_CHECK_NAME, "Check Name"),
        (COL_CHECK_DAILY_VALUE, "Daily Value"),
        (COL_CHECK_MTD_VALUE, "MTD Value"),
        (COL_REVENUE_STATUS, "Revenue"),
        (COL_EPM_STATUS, "EPM"),
        (COL_OVERALL_STATUS, "Overall"),
        (COL_DAILY_REV_TOLERANCE, "ERP Daily Tol"),
        (COL_MTD_REV_TOLERANCE, "ERP MTD Tol"),
        (COL_DAILY_EPM_TOLERANCE, "EPM Daily Tol"),
        (COL_MTD_EPM_TOLERANCE, "EPM MTD Tol"),
        (COL_REV_LIFECYCLE, "Rev Lifecycle"),
        (COL_EPM_LIFECYCLE, "EPM Lifecycle"),
    ]

    display = display.sort_values(
        [COL_REPORTING_DATE, COL_CHECK_NAME],
        ascending=[False, True],
    )

    # Header
    header_cells = ""
    for _, display_name in col_config:
        header_cells += (
            f'<th style="padding:10px 8px;text-align:left;'
            f'border-bottom:2px solid {tokens.border};'
            f'color:{tokens.text_muted};font-size:11px;'
            f'text-transform:uppercase;letter-spacing:.07em;'
            f'background:{tokens.bg_elevated};white-space:nowrap;">'
            f'{display_name}</th>'
        )

    # Body
    body_rows = ""
    for _, row in display.iterrows():
        cells = ""
        for col_name, _ in col_config:
            val = row.get(col_name, "")

            if col_name == COL_REPORTING_DATE and hasattr(val, "strftime"):
                val = val.strftime("%d %b %Y")
            elif col_name in (COL_REVENUE_STATUS, COL_EPM_STATUS, COL_OVERALL_STATUS):
                val = _status_badge(str(val), tokens)
            elif col_name in (COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE):
                val = _lifecycle_badge(str(val), tokens)
            elif col_name in (COL_CHECK_DAILY_VALUE, COL_CHECK_MTD_VALUE):
                val = _fmt_val(val)
            elif col_name in (COL_DAILY_REV_TOLERANCE, COL_MTD_REV_TOLERANCE,
                              COL_DAILY_EPM_TOLERANCE, COL_MTD_EPM_TOLERANCE):
                val = _fmt_tol(val)
            elif col_name == COL_CHECK_NAME:
                val = str(val) if pd.notna(val) else "—"
            else:
                val = str(val) if pd.notna(val) else "—"

            cells += (
                f'<td style="padding:8px;border-bottom:1px solid {tokens.border};'
                f'color:{tokens.text_primary};font-size:12px;'
                f'font-family:{tokens.font_primary};white-space:nowrap;">'
                f'{val}</td>'
            )
        body_rows += f"<tr>{cells}</tr>"

    table_html = f"""
    <div style="overflow-x:auto;border-radius:10px;border:1px solid {tokens.border};">
      <table style="width:100%;border-collapse:collapse;
                     background:{tokens.bg_surface};
                     font-family:{tokens.font_primary};">
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{body_rows}</tbody>
      </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown(
        f'<p style="color:{tokens.text_muted};font-size:11px;margin-top:8px;">'
        f'{len(display)} check(s) across {display[COL_REPORTING_DATE].nunique()} date(s)</p>',
        unsafe_allow_html=True,
    )
