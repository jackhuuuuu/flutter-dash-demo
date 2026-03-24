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
# This matches the original dashboard colours exactly.
FLUTTER_DARK = ThemeTokens(
    # Backgrounds: deep navy, layered from darkest to lightest
    bg_primary="#0B0F1A",
    bg_surface="#131929",
    bg_elevated="#1C2333",
    # Border
    border="#2A3450",
    # Text
    text_primary="#E8EDF5",
    text_muted="#7A8BA8",
    # Semantic colours
    accent="#00D4FF",       # Cyan — brand highlight
    positive="#00E5A0",     # Green — favourable variance
    negative="#FF4D6A",     # Red — adverse variance
    neutral="#7A8BA8",      # Grey — no change
    warning="#FFB300",      # Amber — budget/target
    # Chart series colours (in order: TY, LY, Budget, then extras)
    chart_series=[
        "#00D4FF",  # cyan  — This Year
        "#7A8BA8",  # grey  — Last Year
        "#FFB300",  # amber — Budget
        "#A78BFA",  # purple — extra series
        "#34D399",  # teal  — extra series
        "#FF6B6B",  # coral — extra series
    ],
    chart_grid="#1E2A40",
    # Fonts
    font_primary="DM Sans, system-ui, sans-serif",
    font_mono="JetBrains Mono, monospace",
)


# ── Flutter Light ─────────────────────────────────────────────────────────────
# Optional light theme — useful for printed reports or user preference.
# You can expand this later with your team's preferred light-mode colours.
FLUTTER_LIGHT = ThemeTokens(
    bg_primary="#F5F7FA",
    bg_surface="#FFFFFF",
    bg_elevated="#F0F2F5",
    border="#D1D5DB",
    text_primary="#1F2937",
    text_muted="#6B7280",
    accent="#0EA5E9",
    positive="#059669",
    negative="#DC2626",
    neutral="#6B7280",
    warning="#D97706",
    chart_series=[
        "#0EA5E9",  # blue
        "#9CA3AF",  # grey
        "#D97706",  # amber
        "#7C3AED",  # purple
        "#059669",  # green
        "#DC2626",  # red
    ],
    chart_grid="#E5E7EB",
    font_primary="DM Sans, system-ui, sans-serif",
    font_mono="JetBrains Mono, monospace",
)
