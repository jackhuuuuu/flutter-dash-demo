# flutter_dash/formatters.py
"""
Number and value formatters for finance reporting.

These functions turn raw numbers into human-readable strings for display
in KPI cards, charts, and tables.  They follow finance conventions:
  - Currency: £1.23M, £45.6K, £1,234
  - Percentages: 12.50%
  - Deltas: signed values with direction indicators
  - Margin changes in percentage points (pp)

All formatters handle None gracefully (return "N/A").
"""

from typing import Callable, Tuple


# ── Currency formatter ────────────────────────────────────────────────────────
def fmt_currency(v: float, symbol: str = "£", decimals: int = 0) -> str:
    """
    Format a number as currency with K/M suffixes.

    Examples:
        fmt_currency(1_500_000)     → "£1.50M"
        fmt_currency(45_600)        → "£45.6K"
        fmt_currency(1234)          → "£1,234"
        fmt_currency(1234, "$")     → "$1,234"
        fmt_currency(None)          → "N/A"
    """
    if v is None:
        return "N/A"
    if abs(v) >= 1_000_000:
        return f"{symbol}{v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"{symbol}{v / 1_000:.1f}K"
    return f"{symbol}{v:,.{decimals}f}"


# ── Percentage formatter ──────────────────────────────────────────────────────
def fmt_pct(v: float, decimals: int = 2) -> str:
    """
    Format a decimal as a percentage.

    The input should be a decimal ratio (e.g. 0.125 for 12.5%).

    Examples:
        fmt_pct(0.125)    → "12.50%"
        fmt_pct(0.09, 1)  → "9.0%"
        fmt_pct(None)     → "N/A"
    """
    if v is None:
        return "N/A"
    return f"{v * 100:.{decimals}f}%"


# ── Plain number formatter ────────────────────────────────────────────────────
def fmt_number(v: float, decimals: int = 0) -> str:
    """
    Format a number with K/M suffixes (no currency symbol).

    Examples:
        fmt_number(2_300_000)  → "2.30M"
        fmt_number(45_600)     → "45.6K"
        fmt_number(42)         → "42"
    """
    if v is None:
        return "N/A"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"{v / 1_000:.1f}K"
    return f"{v:,.{decimals}f}"


# ── Comparison formatter (for variance analysis) ─────────────────────────────
def format_comparison(
    ty_value: float,
    ref_value: float,
    formatter: Callable[[float], str],
    is_pct: bool = False,
) -> Tuple[str, str, str, float, float]:
    """
    Calculate and format the variance between two values.

    This is the standard finance variance calculation:
      delta     = TY - Reference (absolute difference)
      delta_pct = delta / |Reference| (relative change)

    For percentage metrics (like margin), the delta is shown in
    percentage points (pp) instead of relative %.

    Parameters
    ----------
    ty_value : float
        This Year's value (or current value).
    ref_value : float
        Reference value (Last Year, Budget, etc.).
    formatter : Callable
        How to format the absolute delta (e.g. fmt_currency, fmt_pct).
    is_pct : bool
        True for percentage metrics (margin) — shows delta in pp.

    Returns
    -------
    tuple of (delta_str, delta_pct_str, ref_str, raw_delta, raw_delta_pct)
        - delta_str: formatted absolute delta (e.g. "£1.2K" or "+0.50pp")
        - delta_pct_str: formatted relative change (e.g. "12.5%")
        - ref_str: formatted reference value
        - raw_delta: numeric delta (for colour-coding)
        - raw_delta_pct: numeric relative delta
    """
    # Calculate deltas
    raw_delta = (ty_value - ref_value) if ref_value else 0.0
    raw_delta_pct = raw_delta / abs(ref_value) if ref_value else 0.0

    # Format reference value
    ref_str = formatter(ref_value)

    # Format the delta
    if is_pct:
        # Margin-type: show change in percentage points (pp)
        delta_str = f"{raw_delta * 100:+.2f}pp"
    else:
        delta_str = formatter(raw_delta)

    # Relative change is always shown as a percentage
    delta_pct_str = f"{raw_delta_pct * 100:.1f}%"

    return delta_str, delta_pct_str, ref_str, raw_delta, raw_delta_pct
