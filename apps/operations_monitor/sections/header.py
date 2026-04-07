# sections/header.py
"""
Dashboard header — shows title, active filters, and latest run timestamp.

This is the top-most section of the Operations Monitor, providing
context about what data the user is viewing.
"""

import streamlit as st
from datetime import date
from typing import Optional

from flutter_dash.theme import get_active_theme


def render_header(
    title: str,
    subtitle: str,
    brand_label: str,
    wallet_label: str,
    latest_run: Optional[str],
    date_range: str,
) -> None:
    """
    Render the dashboard header with title, filter context, and data freshness.

    Parameters
    ----------
    title : str
        Main dashboard heading.
    subtitle : str
        Supporting description text.
    brand_label : str
        Currently selected brand filter label (e.g. "All Brands" or "SBT").
    wallet_label : str
        Currently selected wallet type filter label.
    latest_run : str or None
        Timestamp of the most recent DQ check run (displayed as data freshness).
    date_range : str
        Human-readable date range string (e.g. "07 Mar – 06 Apr 2026").
    """
    tokens = get_active_theme()

    # ── Left side: title and filter context ───────────────────────────────
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown(
            f"""
            <div style="padding:8px 0 4px;">
              <h2 style="color:{tokens.text_primary};font-size:24px;
                         font-weight:700;margin:0;">
                {title}
              </h2>
              <p style="color:{tokens.text_muted};font-size:13px;margin:4px 0 0;">
                {subtitle}
              </p>
              <p style="color:{tokens.text_muted};font-size:13px;margin:4px 0 0;">
                <b style="color:{tokens.accent}">{brand_label}</b>
                &nbsp;|&nbsp;
                <b style="color:{tokens.accent}">{wallet_label}</b>
                &nbsp;|&nbsp;
                {date_range}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Right side: data freshness indicator ──────────────────────────────
    with col_right:
        run_display = latest_run if latest_run else "Unknown"
        st.markdown(
            f"""
            <div style="text-align:right;padding-top:12px;">
              <span style="color:{tokens.text_muted};font-size:12px;">
                Latest run:
                <b style="color:{tokens.text_primary}">{run_display}</b>
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
