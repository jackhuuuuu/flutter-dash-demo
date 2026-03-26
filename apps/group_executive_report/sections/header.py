# dashboards/analytics/sections/header.py
"""
Dashboard header — shows title, active filters, and data-as-of date.
"""

import streamlit as st
from datetime import date

from flutter_dash.theme import get_active_theme


def render_header(
    title: str,
    brand_label: str,
    product_label: str,
    period: str,
    period_start: date,
    period_end: date,
    max_date: date,
) -> None:
    """
    Render the dashboard header with the title, active filter labels,
    and a "Data as of" stamp.
    """
    tokens = get_active_theme()

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(
            f"""
            <div style="padding:8px 0 4px;">
              <h2 style="color:{tokens.text_primary};font-size:24px;font-weight:700;margin:0;">
                {title}
              </h2>
              <p style="color:{tokens.text_muted};font-size:13px;margin:4px 0 0;">
                <b style="color:{tokens.accent}">{brand_label}</b>
                &nbsp;|&nbsp;
                <b style="color:{tokens.accent}">{product_label}</b>
                &nbsp;|&nbsp;
                Period: <b style="color:{tokens.accent}">{period}</b>
                ({period_start.strftime('%d %b')} – {period_end.strftime('%d %b %Y')})
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(
            f'<div style="text-align:right;padding-top:12px;">'
            f'<span style="color:{tokens.text_muted};font-size:12px;">'
            f'Data as of <b style="color:{tokens.text_primary}">{max_date.strftime("%d %b %Y")}</b>'
            f'</span></div>',
            unsafe_allow_html=True,
        )
