# sections/file_detail_table.py
"""
File delivery detail table — shows all file delivery records.

Displays file name, dates, flag, delivery status, and delivery days
in a styled HTML table. Files with EPM-only status are highlighted.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import hex_to_rgba
from flutter_dash.components import section_title

from config import (
    COL_REPORTING_DATE, COL_BRAND, COL_FILE_NAME, COL_CURRENT_FLAG,
    COL_FILE_ERP_STATUS, COL_FILE_EPM_STATUS, COL_FILE_OVERALL_STATUS,
    COL_ERP_DELIVERY_DAYS, COL_EPM_DELIVERY_DAYS, COL_ERP_RESOLUTION_HRS,
    COL_ERP_FINAL_RESENT_AT,
    COL_DELIVERY_LIFECYCLE, COL_LATEST_ROW_COUNT,
    STATUS_FAIL, DELIVERY_EPM_ONLY,
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
    """Return an HTML badge for delivery lifecycle."""
    colour_map = {
        "ERP_DELIVERED": tokens.positive,
        "EPM_ONLY": tokens.warning,
        "MANUAL_OVERRIDE": tokens.accent,
    }
    colour = colour_map.get(lifecycle, tokens.text_muted)
    bg = hex_to_rgba(colour, 0.12)
    label = lifecycle.replace("_", " ").title()
    return (
        f'<span style="background:{bg};color:{colour};padding:2px 8px;'
        f'border-radius:4px;font-size:11px;font-weight:600;">'
        f'{label}</span>'
    )


def render_file_detail_table(df: pd.DataFrame) -> None:
    """
    Render the file delivery detail table.

    Parameters
    ----------
    df : DataFrame
        Filtered file delivery data.
    """
    section_title(
        "File Delivery Detail",
        "All file delivery records for the selected period",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    col_config = [
        (COL_REPORTING_DATE, "Date"),
        (COL_BRAND, "Brand"),
        (COL_FILE_NAME, "File"),
        (COL_CURRENT_FLAG, "Flag"),
        (COL_FILE_ERP_STATUS, "ERP"),
        (COL_FILE_EPM_STATUS, "EPM"),
        (COL_DELIVERY_LIFECYCLE, "Lifecycle"),
        (COL_ERP_DELIVERY_DAYS, "ERP Days"),
        (COL_ERP_RESOLUTION_HRS, "Resolution (hrs)"),
        (COL_ERP_FINAL_RESENT_AT, "Resent At"),
        (COL_LATEST_ROW_COUNT, "Row Count"),
    ]

    display = df.sort_values(
        [COL_REPORTING_DATE, COL_FILE_NAME],
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
            elif col_name in (COL_FILE_ERP_STATUS, COL_FILE_EPM_STATUS):
                val = _status_badge(str(val), tokens)
            elif col_name == COL_DELIVERY_LIFECYCLE:
                val = _lifecycle_badge(str(val), tokens)
            elif col_name == COL_ERP_DELIVERY_DAYS:
                if pd.notna(val):
                    days = int(val)
                    if days > 1:
                        val = (
                            f'<span style="color:{tokens.negative};'
                            f'font-weight:600;">{days} ⚠</span>'
                        )
                    else:
                        val = f"{days}"
                else:
                    val = "—"
            elif col_name == COL_ERP_RESOLUTION_HRS:
                val = f"{val:.1f}" if pd.notna(val) else "—"
            elif col_name == COL_LATEST_ROW_COUNT:
                val = f"{int(val):,}" if pd.notna(val) else "—"
            elif col_name == COL_ERP_FINAL_RESENT_AT:
                if pd.notna(val):
                    ts = str(val)[:19].replace("T", " ")
                    val = (
                        f'<span style="color:{tokens.warning};'
                        f'font-weight:600;">🔄 {ts}</span>'
                    )
                else:
                    val = "—"
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
        f'{len(display)} file(s) across {display[COL_REPORTING_DATE].nunique()} date(s)</p>',
        unsafe_allow_html=True,
    )
