# sections/detail_table.py
"""
Active failures detail table — action-required list.

Shows all checks that are currently failing or have unresolved issues.
This is the "what do I need to fix right now?" table that operators
drill into to understand which checks need attention.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import hex_to_rgba
from flutter_dash.components import section_title

from config import (
    COL_REPORTING_DATE, COL_BRAND, COL_WALLET_TYPE, COL_CHECK_NAME,
    COL_REVENUE_STATUS, COL_EPM_STATUS, COL_OVERALL_STATUS,
    COL_REV_FIRST_FAILED, COL_EPM_FIRST_FAILED,
    COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE,
    COL_REV_RESOLUTION_MINS, COL_EPM_RESOLUTION_MINS,
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


def render_detail_table(df: pd.DataFrame) -> None:
    """
    Render the active failures / issues detail table.

    Shows checks that are either currently FAIL or have UNRESOLVED lifecycle.
    If all checks are healthy, shows a success message instead.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    """
    section_title(
        "Action Required",
        "Checks currently failing or with unresolved issues",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Filter to problems: currently failing OR unresolved ───────────────
    problems = df[
        (df[COL_OVERALL_STATUS] == STATUS_FAIL)
        | (df[COL_REV_LIFECYCLE] == LIFECYCLE_UNRESOLVED)
        | (df[COL_EPM_LIFECYCLE] == LIFECYCLE_UNRESOLVED)
    ].copy()

    if problems.empty:
        st.success("🎉 All checks are passing — no action required!")
        return

    # ── Build the HTML table ──────────────────────────────────────────────
    # Define visible columns and their display names
    col_config = [
        (COL_REPORTING_DATE, "Date"),
        (COL_BRAND, "Brand"),
        (COL_WALLET_TYPE, "Wallet"),
        (COL_CHECK_NAME, "Check Name"),
        (COL_REVENUE_STATUS, "Revenue"),
        (COL_EPM_STATUS, "EPM"),
        (COL_OVERALL_STATUS, "Overall"),
        (COL_REV_LIFECYCLE, "Rev Lifecycle"),
        (COL_EPM_LIFECYCLE, "EPM Lifecycle"),
    ]

    # Sort by date descending, then check name
    problems = problems.sort_values(
        [COL_REPORTING_DATE, COL_CHECK_NAME],
        ascending=[False, True],
    )

    # ── Table header ──────────────────────────────────────────────────────
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

    # ── Table body ────────────────────────────────────────────────────────
    body_rows = ""
    for _, row in problems.iterrows():
        cells = ""
        for col_name, _ in col_config:
            val = row.get(col_name, "")

            # Format date
            if col_name == COL_REPORTING_DATE and hasattr(val, "strftime"):
                val = val.strftime("%d %b %Y")

            # Render status columns as badges
            if col_name in (COL_REVENUE_STATUS, COL_EPM_STATUS, COL_OVERALL_STATUS):
                val = _status_badge(str(val), tokens)
            elif col_name in (COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE):
                val = _lifecycle_badge(str(val), tokens)
            else:
                val = str(val) if pd.notna(val) else "—"

            cells += (
                f'<td style="padding:8px;border-bottom:1px solid {tokens.border};'
                f'color:{tokens.text_primary};font-size:12px;'
                f'font-family:{tokens.font_primary};white-space:nowrap;">'
                f'{val}</td>'
            )
        body_rows += f"<tr>{cells}</tr>"

    # ── Full table HTML ───────────────────────────────────────────────────
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

    # ── Summary line below the table ──────────────────────────────────────
    st.markdown(
        f'<p style="color:{tokens.text_muted};font-size:11px;margin-top:8px;">'
        f'{len(problems)} issue(s) found across {problems[COL_REPORTING_DATE].nunique()} date(s)</p>',
        unsafe_allow_html=True,
    )
