# hub/app.py
"""
FBI Hub — Financial BI Hub Landing Page.

Central launcher for all FBI team dashboards and apps.
Each app is a separate Databricks App with its own permissions
and fault isolation. This hub provides a unified entry point
with search, theming, and app discovery.

Run locally:
    cd hub
    streamlit run app.py --server.port 8501

In production, this is deployed as its own Databricks App.
"""

import os
import streamlit as st

from flutter_dash.theme import apply_theme
from flutter_dash.theme.palettes import FLUTTER_DARK, FLUTTER_LIGHT
from flutter_dash.theme.css import generate_css
from flutter_dash.theme.tokens import hex_to_rgba

from hub_config import SECTIONS, APPS


# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

HUB_TITLE = "FBI Hub"
HUB_SUBTITLE = "Financial BI Hub — Flutter UK&I"
HUB_PAGE_ICON = "🏠"

# Base URL for apps. In production (Databricks), override via environment variable.
# For local dev, apps run on localhost with different ports.
LOCAL_BASE_URL = "http://localhost"
DATABRICKS_BASE_URL = os.environ.get("DATABRICKS_APPS_BASE_URL", "")


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def _get_app_url(app: dict, theme: str) -> str:
    """
    Build the launch URL for an app.

    - If the app has a "url" key, use it directly (external apps).
    - If running on Databricks (DATABRICKS_BASE_URL is set), build from that.
    - Otherwise, build a localhost URL using the app's local_port.

    The current theme is appended as a query parameter for internal apps,
    so dashboards inherit the user's chosen theme from the hub.
    """
    if "url" in app:
        return app["url"]

    if DATABRICKS_BASE_URL:
        base = f"{DATABRICKS_BASE_URL}/{app['app_path']}"
    else:
        base = f"{LOCAL_BASE_URL}:{app['local_port']}"

    # Pass theme to internal apps
    if app.get("internal", False):
        base += f"?theme={theme}"

    return base


def _render_logo(tokens) -> None:
    """
    Render the Flutter logo banner at the top of the hub.

    Tries to load the logo image from hub/assets/flutter_logo.png.
    Falls back to a styled text banner if the image is not found.
    """
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "flutter_logo.png")

    if os.path.exists(logo_path):
        # Use columns to control logo size and add the hub title beside it
        col_logo, col_title = st.columns([1, 3])
        with col_logo:
            st.image(logo_path, width=160)
        with col_title:
            st.markdown(
                f"""
                <div style="display:flex;flex-direction:column;justify-content:center;
                            height:100%;padding:8px 0;">
                    <h1 style="color:{tokens.text_primary};font-size:28px;
                               font-weight:700;margin:0;">
                        {HUB_TITLE}
                    </h1>
                    <p style="color:{tokens.text_muted};font-size:14px;margin:4px 0 0;">
                        {HUB_SUBTITLE}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        # Fallback: text-only banner
        st.markdown(
            f"""
            <div style="padding:16px 0 8px;">
                <h1 style="color:{tokens.text_primary};font-size:28px;
                           font-weight:700;margin:0;">
                    🏠 {HUB_TITLE}
                </h1>
                <p style="color:{tokens.text_muted};font-size:14px;margin:4px 0 0;">
                    {HUB_SUBTITLE}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_app_tile(app: dict, theme: str, tokens) -> None:
    """
    Render a single app tile card.

    Shows the app icon, title, description, status badge, and launch link.
    Live apps get a clickable link; Coming Soon apps show a disabled badge.
    """
    is_live = app["status"] == "live"
    url = _get_app_url(app, theme) if is_live else "#"

    # Status badge
    if is_live:
        badge_bg = hex_to_rgba(tokens.positive, 0.15)
        badge_color = tokens.positive
        badge_text = "● Live"
    else:
        badge_bg = hex_to_rgba(tokens.text_muted, 0.15)
        badge_color = tokens.text_muted
        badge_text = "◌ Coming Soon"

    # Card opacity for coming-soon apps
    opacity = "1" if is_live else "0.55"

    # Link or disabled state
    if is_live:
        link_html = (
            f'<a href="{url}" target="_blank" '
            f'style="display:inline-block;margin-top:12px;padding:6px 16px;'
            f"background:{hex_to_rgba(tokens.accent, 0.12)};"
            f"color:{tokens.accent};border:1px solid {hex_to_rgba(tokens.accent, 0.3)};"
            f'border-radius:8px;text-decoration:none;font-size:12px;'
            f'font-weight:600;letter-spacing:0.03em;">Launch →</a>'
        )
    else:
        link_html = ""

    st.markdown(
        f"""
        <div style="background:{tokens.bg_surface};border:1px solid {tokens.border};
                    border-radius:14px;padding:20px;opacity:{opacity};
                    height:100%;display:flex;flex-direction:column;">
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:10px;">
                <span style="font-size:28px;">{app['icon']}</span>
                <span style="background:{badge_bg};color:{badge_color};
                             font-size:11px;font-weight:600;padding:3px 10px;
                             border-radius:12px;">{badge_text}</span>
            </div>
            <h3 style="color:{tokens.text_primary};font-size:16px;font-weight:600;
                       margin:0 0 6px;">{app['title']}</h3>
            <p style="color:{tokens.text_muted};font-size:13px;margin:0;flex:1;">
                {app['description']}</p>
            {link_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═════════════════════════════════════════════════════════════════════════════

# ── Theme setup ───────────────────────────────────────────────────────────────
# Default to light theme. Can be overridden via URL param ?theme=dark.
if "theme" not in st.session_state:
    theme_param = st.query_params.get("theme", "light")
    st.session_state.theme = theme_param if theme_param in ("light", "dark") else "light"

_palette = FLUTTER_LIGHT if st.session_state.theme == "light" else FLUTTER_DARK
apply_theme(st, _palette, page_title=HUB_TITLE, page_icon=HUB_PAGE_ICON)
tokens = _palette

# ── Top bar: search + theme toggle ───────────────────────────────────────────
_col_spacer, _col_search, _col_theme = st.columns([5, 5, 1])

with _col_search:
    search_query = st.text_input(
        "Search apps",
        placeholder="🔍  Search dashboards and apps...",
        label_visibility="collapsed",
    )

with _col_theme:
    _is_dark = st.session_state.theme == "dark"
    if st.button("☀️" if _is_dark else "🌙", key="theme_toggle"):
        st.session_state.theme = "light" if _is_dark else "dark"
        st.rerun()

# ── Logo banner ───────────────────────────────────────────────────────────────
_render_logo(tokens)

st.markdown(
    f'<div style="height:2px;margin:8px 0 24px;'
    f'background:linear-gradient(90deg,{tokens.accent},transparent);"></div>',
    unsafe_allow_html=True,
)

# ── Filter apps by search ────────────────────────────────────────────────────
if search_query:
    q = search_query.lower()
    filtered_apps = [
        a for a in APPS
        if q in a["title"].lower() or q in a["description"].lower()
    ]
else:
    filtered_apps = APPS

# ── Render sections ──────────────────────────────────────────────────────────
for section in SECTIONS:
    section_apps = [a for a in filtered_apps if a["section"] == section["id"]]

    # Skip empty sections (no matching apps after search filter)
    if not section_apps:
        continue

    # Section header
    st.markdown(
        f"""
        <div style="margin:24px 0 16px;">
            <h2 style="color:{tokens.text_primary};font-size:16px;font-weight:600;
                       text-transform:uppercase;letter-spacing:0.1em;margin:0;">
                {section['icon']}  {section['title']}
            </h2>
            <p style="color:{tokens.text_muted};font-size:13px;margin:4px 0 0;">
                {section['subtitle']}
            </p>
            <div style="height:2px;margin-top:8px;
                background:linear-gradient(90deg,{tokens.accent},transparent);"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # App tiles in a responsive grid (3 columns)
    cols = st.columns(3)
    for i, app in enumerate(section_apps):
        with cols[i % 3]:
            _render_app_tile(app, st.session_state.theme, tokens)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="margin-top:48px;padding:16px 0;border-top:1px solid {tokens.border};
                text-align:center;">
        <p style="color:{tokens.text_muted};font-size:11px;margin:0;">
            FBI Hub — Flutter UK&I Financial BI Team
            &nbsp;|&nbsp; Powered by Databricks Apps
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
