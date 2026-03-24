# flutter_dash/components/section_title.py
"""
Section title — styled header with accent underline.

Use this to visually separate dashboard sections (e.g. "Key Metrics",
"Daily Trend", "Brand Breakdown").
"""

import streamlit as st

from flutter_dash.theme import get_active_theme


def section_title(text: str, subtitle: str = "", tokens=None) -> None:
    """
    Render a styled section title with optional subtitle.

    Parameters
    ----------
    text : str
        Main title text (displayed in uppercase).
    subtitle : str, optional
        Supporting text below the title.
    tokens : ThemeTokens, optional
        Theme palette. Defaults to the active theme.
    """
    if tokens is None:
        tokens = get_active_theme()

    sub_html = ""
    if subtitle:
        sub_html = (
            f'<p style="color:{tokens.text_muted};font-size:13px;'
            f'margin:4px 0 0;">{subtitle}</p>'
        )

    st.markdown(
        f"""
        <div style="margin:24px 0 16px;">
          <h3 style="color:{tokens.text_primary};font-size:14px;font-weight:600;
                     text-transform:uppercase;letter-spacing:.1em;margin:0;">
            {text}
          </h3>
          {sub_html}
          <div style="height:2px;margin-top:8px;
            background:linear-gradient(90deg,{tokens.accent},transparent);"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
