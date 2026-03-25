# flutter_dash/theme/tokens.py
"""
ThemeTokens — the "contract" that every theme palette must fill.

This is a dataclass (like a structured template) that defines every colour
and font a dashboard needs.  When you create a new palette, you fill in
all these fields.  Components read from these fields, so they automatically
adapt to whatever palette is active.

Why a dataclass instead of a plain dict?
  - Your IDE shows autocomplete when you type `tokens.` (try it!)
  - Typos are caught immediately — e.g. `tokens.accen` → error, not silent None
  - Easy to see all available fields in one place
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)  # frozen=True means values can't be changed after creation
class ThemeTokens:
    """
    Complete visual identity for a dashboard.

    Organised into logical groups:
      - Backgrounds: layered surfaces (primary → surface → elevated)
      - Text: primary text and muted/secondary text
      - Semantic: colours that carry meaning (green = good, red = bad, etc.)
      - Chart: colours for chart series, gridlines
      - Fonts: typeface families
    """

    # ── Backgrounds (darkest → lightest in dark mode) ─────────────────────────
    bg_primary: str    # Main page background (darkest)
    bg_surface: str    # Cards, sidebar, chart backgrounds
    bg_elevated: str   # Hover states, dropdowns, tooltips

    # ── Borders ───────────────────────────────────────────────────────────────
    border: str        # Dividers, card outlines, table grid lines

    # ── Text ──────────────────────────────────────────────────────────────────
    text_primary: str  # Main readable text (headlines, values)
    text_muted: str    # Secondary/supporting text (labels, captions)

    # ── Semantic colours (finance standard: green = favourable) ───────────────
    accent: str        # Brand highlight, links, active elements
    positive: str      # Favourable variance (green)
    negative: str      # Adverse variance (red)
    neutral: str       # No change / not applicable (grey)
    warning: str       # Budget/target indicators (amber/gold)

    # ── Chart colours ─────────────────────────────────────────────────────────
    # Ordered list of colours for multi-series charts.
    # First colour = primary series (TY), second = secondary (LY), etc.
    chart_series: List[str] = field(default_factory=lambda: [
        "#00D4FF",  # cyan  — This Year
        "#7A8BA8",  # grey  — Last Year
        "#FFB300",  # amber — Budget
        "#A78BFA",  # purple
        "#34D399",  # teal
        "#FF6B6B",  # coral
    ])
    chart_grid: str = "#1E2A40"  # Gridlines on charts

    # ── Fonts ─────────────────────────────────────────────────────────────────
    font_primary: str = "DM Sans, system-ui, sans-serif"  # Body & headings
    font_mono: str = "JetBrains Mono, monospace"           # Numbers in tables


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert #RRGGBB to rgba(r,g,b,alpha) for use in CSS/HTML."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
