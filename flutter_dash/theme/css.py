# flutter_dash/theme/css.py
"""
CSS generator — builds Streamlit CSS from theme tokens.

Instead of one giant hardcoded CSS string, this function takes a ThemeTokens
and produces the CSS dynamically.  If you switch palettes (e.g. dark → light),
the CSS updates automatically.

You never need to edit this file for a new dashboard — just pass different
ThemeTokens to apply_theme() and the CSS adapts.
"""

from flutter_dash.theme.tokens import ThemeTokens


def generate_css(tokens: ThemeTokens) -> str:
    """
    Build the full Streamlit CSS string from theme tokens.

    This CSS controls:
      - Page background and font
      - Sidebar styling
      - Input widget styling (dropdowns, multiselects)
      - Chart container rounding
      - Scrollbar appearance
      - Hide default Streamlit menu/footer
    """
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

  /* ── Custom scrollbar ────────────────────────────────────────────────────── */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: {tokens.bg_primary}; }}
  ::-webkit-scrollbar-thumb {{ background: {tokens.border}; border-radius: 3px; }}
</style>
"""
