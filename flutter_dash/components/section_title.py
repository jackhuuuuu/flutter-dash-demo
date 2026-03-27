# flutter_dash/components/section_title.py
"""
Section title — styled header with accent underline.

Use this to visually separate dashboard sections (e.g. "Key Metrics",
"Daily Trend", "Brand Breakdown").

Also provides multi_section_title() for sections with multiple charts
side-by-side, rendering one title per chart aligned to the column layout.
"""

import streamlit as st
from typing import List, Optional, Tuple

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import ThemeTokens


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


def multi_section_title(
    titles: List[Tuple[str, str]],
    col_ratios: Optional[List[int]] = None,
    tokens=None,
) -> None:
    """
    Render multiple section titles side-by-side, aligned to chart columns.

    Parameters
    ----------
    titles : list of (title, subtitle) tuples
        One title per chart column.
    col_ratios : list of int, optional
        Column width ratios (e.g. [3, 2]). Defaults to equal widths.
    tokens : ThemeTokens, optional
        Theme palette. Defaults to the active theme.
    """
    if tokens is None:
        tokens = get_active_theme()
    if col_ratios is None:
        col_ratios = [1] * len(titles)

    cols = st.columns(col_ratios)
    for col, (text, subtitle) in zip(cols, titles):
        sub_html = ""
        if subtitle:
            sub_html = (
                f'<p style="color:{tokens.text_muted};font-size:13px;'
                f'margin:4px 0 0;">{subtitle}</p>'
            )
        col.markdown(
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
