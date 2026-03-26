# flutter_dash/theme/css.py
"""
CSS generator — builds Streamlit CSS from theme tokens.

Instead of one giant hardcoded CSS string, this function takes a ThemeTokens
and produces the CSS dynamically.  If you switch palettes (e.g. dark → light),
the CSS updates automatically.

You never need to edit this file for a new dashboard — just pass different
ThemeTokens to apply_theme() and the CSS adapts.
"""

from flutter_dash.theme.tokens import ThemeTokens, hex_to_rgba


def generate_css(tokens: ThemeTokens) -> str:
    """
    Build the full Streamlit CSS string from theme tokens.

    This CSS controls:
      - Page background and font
      - Sidebar styling
      - Input widget styling (dropdowns, multiselects)
      - Multiselect tag/pill colours
      - Chart container rounding
      - Scrollbar appearance
      - Hide default Streamlit menu/footer
    """
    tag_bg = hex_to_rgba(tokens.accent, 0.15)
    tag_border = hex_to_rgba(tokens.accent, 0.30)

    return f"""
<style>
  /* ── Page background & typography ────────────────────────────────────────── */
  .stApp {{
    background-color: {tokens.bg_primary};
    font-family: {tokens.font_primary};
    color: {tokens.text_primary};
  }}

  /* ── Sidebar toggle button (visible even when sidebar is collapsed) ──────── */
  [data-testid="collapsedControl"] {{
    display: block !important;
    visibility: visible !important;
    background-color: {tokens.bg_surface} !important;
    border: 1px solid {tokens.border} !important;
    border-radius: 0 8px 8px 0 !important;
    color: {tokens.accent} !important;
    z-index: 999 !important;
  }}

  /* ── Sidebar ─────────────────────────────────────────────────────────────── */
  [data-testid="stSidebar"] {{
    background-color: {tokens.bg_surface} !important;
    border-right: 1px solid {tokens.border};
  }}
  [data-testid="stSidebar"] * {{
    color: {tokens.text_primary} !important;
  }}
  [data-testid="stSidebar"] > div:first-child {{
    background-color: {tokens.bg_surface} !important;
  }}

  /* ── Sidebar widget internals ────────────────────────────────────────────── */
  [data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: {tokens.bg_elevated} !important;
    border-color: {tokens.border} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="input"] {{
    background-color: {tokens.bg_elevated} !important;
    border-color: {tokens.border} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="input"] input {{
    color: {tokens.text_primary} !important;
    -webkit-text-fill-color: {tokens.text_primary} !important;
  }}

  /* ── Multiselect tag pills ───────────────────────────────────────────────── */
  [data-baseweb="tag"] {{
    background-color: {tag_bg} !important;
    border: 1px solid {tag_border} !important;
    border-radius: 6px !important;
  }}
  [data-baseweb="tag"] span,
  [data-baseweb="tag"] div {{
    color: {tokens.accent} !important;
  }}
  [data-baseweb="tag"] [role="presentation"] svg {{
    fill: {tokens.accent} !important;
  }}

  /* ── Dropdown / popover menus ────────────────────────────────────────────── */
  [data-baseweb="popover"] > div {{
    background-color: {tokens.bg_elevated} !important;
    border: 1px solid {tokens.border} !important;
    border-radius: 8px !important;
  }}
  ul[role="listbox"] {{
    background-color: {tokens.bg_elevated} !important;
  }}
  ul[role="listbox"] li {{
    color: {tokens.text_primary} !important;
  }}
  ul[role="listbox"] li:hover {{
    background-color: {tokens.bg_surface} !important;
  }}

  /* ── Metric containers ───────────────────────────────────────────────────── */
  [data-testid="metric-container"] {{
    background-color: {tokens.bg_surface};
    border: 1px solid {tokens.border};
    border-radius: 12px;
    padding: 16px;
  }}

  /* ── Data tables ─────────────────────────────────────────────────────────── */
  .stDataFrame {{
    border: 1px solid {tokens.border};
    border-radius: 8px;
  }}

  /* ── Dropdown and multiselect widgets ────────────────────────────────────── */
  .stSelectbox > div > div,
  .stMultiSelect > div > div {{
    background-color: {tokens.bg_elevated} !important;
    border-color: {tokens.border} !important;
    color: {tokens.text_primary} !important;
  }}

  /* ── Plotly chart containers ─────────────────────────────────────────────── */
  .js-plotly-plot {{
    border-radius: 12px;
    overflow: hidden;
  }}

  /* ── Horizontal rules ────────────────────────────────────────────────────── */
  hr {{
    border-color: {tokens.border};
    margin: 24px 0;
  }}

  /* ── Hide default Streamlit branding ─────────────────────────────────────── */
  #MainMenu, footer {{ visibility: hidden; }}

  /* ── Top header bar ──────────────────────────────────────────────────────── */
  header[data-testid="stHeader"] {{
    background-color: rgba(0,0,0,0) !important;
    color: {tokens.accent} !important;
  }}

  /* ── Sidebar collapse button ─────────────────────────────────────────────── */
  button[data-testid="stSidebarCollapseButton"] {{
    color: {tokens.accent} !important;
    background-color: {tokens.bg_surface} !important;
    border: 1px solid {tokens.border} !important;
  }}

  /* ── Global text inputs (search bars, form fields) ───────────────────────── */
  [data-baseweb="input"] {{
    background-color: {tokens.bg_elevated} !important;
    border-color: {tokens.border} !important;
  }}
  [data-baseweb="input"] input {{
    color: {tokens.text_primary} !important;
    -webkit-text-fill-color: {tokens.text_primary} !important;
  }}
  [data-baseweb="input"] input::placeholder {{
    color: {tokens.text_muted} !important;
    -webkit-text-fill-color: {tokens.text_muted} !important;
    opacity: 1 !important;
  }}
  .stTextInput > div > div {{
    background-color: {tokens.bg_elevated} !important;
    border-color: {tokens.border} !important;
    border-radius: 8px !important;
  }}

  /* ── Global buttons (prevent black bg everywhere) ────────────────────────── */
  .stButton > button {{
    background-color: {tokens.bg_elevated} !important;
    color: {tokens.text_primary} !important;
    border: 1px solid {tokens.border} !important;
    border-radius: 8px !important;
  }}
  .stButton > button:hover {{
    background-color: {tokens.bg_surface} !important;
    border-color: {tokens.accent} !important;
  }}

  /* ── All buttons (catch-all to prevent black bg leakage) ──────────────── */
  [data-testid="stSidebar"] button,
  [data-testid="stSidebar"] .stButton > button {{
    background-color: {tokens.bg_elevated} !important;
    color: {tokens.text_primary} !important;
    border: 1px solid {tokens.border} !important;
    border-radius: 8px !important;
  }}
  [data-testid="stSidebar"] .stButton > button:hover {{
    background-color: {tokens.bg_surface} !important;
    border-color: {tokens.accent} !important;
  }}

  /* ── Theme toggle button (icon-only, compact) ────────────────────────────── */
  [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"][kind="secondary"] {{
    background-color: {tokens.bg_elevated} !important;
    border: 1px solid {tokens.border} !important;
    border-radius: 10px !important;
    font-size: 20px !important;
    line-height: 1 !important;
    padding: 6px 12px !important;
    min-height: 0 !important;
    width: auto !important;
  }}

  /* ── Custom scrollbar ────────────────────────────────────────────────────── */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: {tokens.bg_primary}; }}
  ::-webkit-scrollbar-thumb {{ background: {tokens.border}; border-radius: 3px; }}
</style>
"""
