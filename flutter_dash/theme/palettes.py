# flutter_dash/theme/palettes.py
"""
Pre-built theme palettes.

Each palette is a ThemeTokens instance with all colours and fonts filled in.
To create a custom palette, copy one and change the values you want.

Available palettes:
  - FLUTTER_DARK  — Dark theme (current default)
  - FLUTTER_LIGHT — Light theme (for printed reports or light-mode preference)
"""

from flutter_dash.theme.tokens import ThemeTokens

# ── Flutter Dark ──────────────────────────────────────────────────────────────
# Flutter Entertainment brand dark theme.
# Navy-anchored palette built from Flutter's corporate identity:
#   - Deep Space navy backgrounds (#051324 → #0B1F38 → #1A2540)
#   - Electric Cyan hero accent (#00D4FF)
#   - Sky Blue secondary (#7AB7E2)
#   - Standard finance status colours (mint ✓, coral ✗, amber ⚠)
FLUTTER_DARK = ThemeTokens(
    # Backgrounds: Flutter Navy, layered from deepest to lightest
    bg_primary="#051324",       # Flutter Deep Space — page background
    bg_surface="#0B1F38",       # Cards, sidebar, chart backgrounds
    bg_elevated="#1A2540",      # Dropdowns, hover states, tooltips (Deep Slate)
    # Border
    border="#1E3A5F",           # Navy-tinted borders and dividers
    # Text
    text_primary="#FFFFFF",     # Pure White — headlines and values
    text_muted="#8BAFC4",       # Muted sky blue — labels, captions
    # Semantic colours
    accent="#00D4FF",           # Electric Cyan — brand hero colour
    positive="#00E5A0",         # Bright mint green — favourable
    negative="#FF4D6A",         # Soft coral red — adverse
    neutral="#8BAFC4",          # Muted sky blue — no change
    warning="#FFB300",          # Bright amber/gold — budget/target
    # Chart series colours (in order: TY, LY, Budget, then extras)
    chart_series=[
        "#00D4FF",  # Electric Cyan  — This Year
        "#7AB7E2",  # Sky Blue       — Last Year
        "#FFB300",  # Amber          — Budget
        "#A78BFA",  # Purple         — extra series
        "#34D399",  # Teal           — extra series
        "#FF6B6B",  # Coral          — extra series
    ],
    chart_grid="#1A2540",       # Deep Slate gridlines
    # Fonts
    font_primary="DM Sans, system-ui, sans-serif",
    font_mono="JetBrains Mono, monospace",
)


# ── Flutter Light ─────────────────────────────────────────────────────────────
# Flutter Entertainment brand light theme.
# Inverts the dark palette for light-mode UIs or printed reports.
# Uses Flutter Navy for text and a cooler blue-grey surface stack.
FLUTTER_LIGHT = ThemeTokens(
    bg_primary="#F0F4F8",       # Cool blue-grey page background
    bg_surface="#FFFFFF",       # Pure white cards
    bg_elevated="#E8EFF5",      # Light blue-grey hover states
    border="#C8D6E0",           # Soft navy border
    text_primary="#051324",     # Flutter Navy — primary text
    text_muted="#5A7A94",       # Muted navy — labels, captions
    accent="#0094CC",           # Deeper cyan for readability on white
    positive="#059669",         # Dark mint — favourable
    negative="#DC2626",         # Dark red — adverse
    neutral="#5A7A94",          # Muted navy — neutral
    warning="#D97706",          # Dark amber — budget/target
    chart_series=[
        "#0094CC",  # Cyan        — This Year
        "#7AB7E2",  # Sky Blue    — Last Year
        "#D97706",  # Amber       — Budget
        "#7C3AED",  # Purple      — extra series
        "#059669",  # Green       — extra series
        "#DC2626",  # Red         — extra series
    ],
    chart_grid="#E0E8EF",       # Soft gridlines
    font_primary="DM Sans, system-ui, sans-serif",
    font_mono="JetBrains Mono, monospace",
)
