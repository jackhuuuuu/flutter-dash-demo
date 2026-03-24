# flutter_dash/theme/__init__.py
"""
Theme system — apply a consistent visual identity to any Streamlit dashboard.

Usage:
    from flutter_dash.theme import apply_theme
    apply_theme(st, page_title="My Dashboard")
"""

import streamlit as st

from flutter_dash.theme.tokens import ThemeTokens
from flutter_dash.theme.palettes import FLUTTER_DARK
from flutter_dash.theme.css import generate_css

# ── Module-level "active theme" ───────────────────────────────────────────────
# This stores whichever theme the dashboard chose via apply_theme().
# Other modules (components, charts) read from here so they automatically
# pick up the right colours without you passing tokens everywhere.
_active_theme: ThemeTokens = FLUTTER_DARK


def get_active_theme() -> ThemeTokens:
    """Return the currently active theme tokens."""
    return _active_theme


def apply_theme(
    st_module=None,
    tokens: ThemeTokens | None = None,
    page_title: str = "Dashboard",
    page_icon: str = "📊",
    layout: str = "wide",
) -> None:
    """
    One-call setup for any Streamlit dashboard.

    What it does:
      1. Sets the Streamlit page config (title, icon, layout)
      2. Injects the themed CSS into the page

    Parameters
    ----------
    st_module : streamlit
        Pass the `st` module from your app. If None, imports streamlit itself.
    tokens : ThemeTokens, optional
        A custom palette. Defaults to FLUTTER_DARK (the standard dark theme).
    page_title : str
        Browser tab title.
    page_icon : str
        Browser tab icon (emoji or URL).
    layout : str
        "wide" or "centered".
    """
    global _active_theme

    if st_module is None:
        st_module = st

    # Use the provided tokens, or fall back to the dark theme
    if tokens is not None:
        _active_theme = tokens
    else:
        _active_theme = FLUTTER_DARK

    # Set Streamlit's page config (must be the first Streamlit call in the app)
    st_module.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )

    # Inject the themed CSS
    css = generate_css(_active_theme)
    st_module.markdown(css, unsafe_allow_html=True)
