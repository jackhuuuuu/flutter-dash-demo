# flutter_dash/theme/css.py
"""
CSS generator — builds Streamlit CSS from theme tokens.

Takes a ThemeTokens palette and produces the full CSS for a Streamlit app.
When you switch palettes (e.g. dark → light), the CSS adapts automatically.

You never need to edit this file for a new dashboard — just pass different
ThemeTokens to apply_theme() and the CSS adapts.

Sections (in order):
  1. Page — background, font, branding
  2. Header — top bar, sidebar collapse/expand buttons
  3. Sidebar — background, widgets, buttons
  4. Widgets — dropdowns, multiselects, tags, text inputs
  5. Content — charts, tables, metric containers
  6. Scrollbar
"""

from flutter_dash.theme.tokens import ThemeTokens, hex_to_rgba


def generate_css(tokens: ThemeTokens) -> str:
    """Build the full Streamlit CSS string from theme tokens."""
    tag_bg = hex_to_rgba(tokens.accent, 0.15)
    tag_border = hex_to_rgba(tokens.accent, 0.30)

    return f"""
<style>
  /* ═══════════════════════════════════════════════════════════════════════════
     1. PAGE — background, typography, branding
     ═══════════════════════════════════════════════════════════════════════════ */

  .stApp {{
    background-color: {tokens.bg_primary};
    font-family: {tokens.font_primary};
    color: {tokens.text_primary};
  }}

  #MainMenu, footer {{ visibility: hidden; }}

  hr {{
    border-color: {tokens.border};
    margin: 24px 0;
  }}

  /* ═══════════════════════════════════════════════════════════════════════════
     2. HEADER — top bar, sidebar expand/collapse buttons
     ═══════════════════════════════════════════════════════════════════════════ */

  header[data-testid="stHeader"] {{
    background-color: rgba(0,0,0,0) !important;
  }}

  /* Both sidebar buttons share the same style: text_primary arrows on
     bg_surface background. The expand button (collapsedControl) lives
     outside the sidebar; the collapse button (stSidebarCollapseButton)
     lives in the header. We target all descendants to override any
     Streamlit inline styles. */

  [data-testid="collapsedControl"] {{
    display: block !important;
    visibility: visible !important;
    background-color: {tokens.bg_surface} !important;
    border: 1px solid {tokens.border} !important;
    border-radius: 0 8px 8px 0 !important;
    z-index: 999 !important;
  }}

  [data-testid="collapsedControl"] button {{
    background-color: {tokens.bg_surface} !important;
    border: none !important;
  }}

  button[data-testid="stSidebarCollapseButton"] {{
    background-color: {tokens.bg_surface} !important;
    border: 1px solid {tokens.border} !important;
  }}

  /* Force arrow colour on every descendant of both buttons */
  [data-testid="collapsedControl"] *,
  [data-testid="collapsedControl"] *::before,
  [data-testid="collapsedControl"] *::after,
  button[data-testid="stSidebarCollapseButton"] *,
  header[data-testid="stHeader"] button,
  header[data-testid="stHeader"] button * {{
    color: {tokens.text_primary} !important;
    fill: {tokens.text_primary} !important;
    stroke: {tokens.text_primary} !important;
    -webkit-text-fill-color: {tokens.text_primary} !important;
  }}

  /* Hover state for both buttons */
  [data-testid="collapsedControl"] button:hover,
  button[data-testid="stSidebarCollapseButton"]:hover {{
    background-color: {tokens.bg_elevated} !important;
  }}

  /* ═══════════════════════════════════════════════════════════════════════════
     3. SIDEBAR — background, text, buttons
     ═══════════════════════════════════════════════════════════════════════════ */

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

  /* Sidebar select/input widgets */
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

  /* Sidebar buttons */
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

  /* Theme toggle button (compact icon style) */
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

  /* ═══════════════════════════════════════════════════════════════════════════
     4. WIDGETS — dropdowns, multiselects, tags, text inputs, buttons
     ═══════════════════════════════════════════════════════════════════════════ */

  /* Dropdown and multiselect containers */
  .stSelectbox > div > div,
  .stMultiSelect > div > div {{
    background-color: {tokens.bg_elevated} !important;
    border-color: {tokens.border} !important;
    color: {tokens.text_primary} !important;
  }}

  /* Multiselect tag pills */
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

  /* Dropdown / popover menus */
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

  /* Text inputs */
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

  /* Global buttons */
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

  /* ═══════════════════════════════════════════════════════════════════════════
     5. CONTENT — charts, tables, metric containers
     ═══════════════════════════════════════════════════════════════════════════ */

  [data-testid="metric-container"] {{
    background-color: {tokens.bg_surface};
    border: 1px solid {tokens.border};
    border-radius: 12px;
    padding: 16px;
  }}

  .js-plotly-plot {{
    border-radius: 12px;
    overflow: hidden;
  }}

  .stDataFrame {{
    border: 1px solid {tokens.border};
    border-radius: 8px;
  }}

  /* ═══════════════════════════════════════════════════════════════════════════
     6. SCROLLBAR
     ═══════════════════════════════════════════════════════════════════════════ */

  /* Firefox */
  * {{
    scrollbar-color: {tokens.neutral} {tokens.bg_surface};
    scrollbar-width: thin;
  }}

  /* WebKit (Chrome, Edge, Safari) */
  ::-webkit-scrollbar {{ width: 8px; }}
  ::-webkit-scrollbar-track {{ background: {tokens.bg_surface}; }}
  ::-webkit-scrollbar-thumb {{ background: {tokens.neutral}; border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: {tokens.text_muted}; }}
</style>
"""
