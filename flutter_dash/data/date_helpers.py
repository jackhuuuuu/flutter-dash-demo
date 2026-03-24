# flutter_dash/data/date_helpers.py
"""
Pure date-range helpers for period calculations.

These functions have NO global state — pass in the reference date (usually
the most recent date in your dataset) and get back a (start, end) tuple.

Supported periods:
  Yesterday, WTD (week-to-date), MTD (month-to-date),
  QTD (quarter-to-date), YTD (year-to-date), Last 7 days, Last 30 days.

Usage:
    from flutter_dash.data.date_helpers import get_period_dates
    start, end = get_period_dates(max_date, "MTD")
"""

from __future__ import annotations

from datetime import date, timedelta


# ── Standard period options (used by SidebarBuilder defaults) ─────────────────
PERIOD_OPTIONS: list[str] = [
    "Yesterday",
    "WTD",
    "MTD",
    "QTD",
    "YTD",
    "Last 7 days",
    "Last 30 days",
]


def _quarter_start(d: date) -> date:
    """Return the first day of the calendar quarter containing *d*."""
    q_month = ((d.month - 1) // 3) * 3 + 1
    return d.replace(month=q_month, day=1)


def get_period_dates(max_date: date, period: str) -> tuple[date, date]:
    """
    Return ``(start_date, end_date)`` for a named period relative to
    *max_date*.

    Parameters
    ----------
    max_date : date
        The latest available date in the dataset (anchor point).
    period : str
        One of the keys in :data:`PERIOD_OPTIONS`.

    Returns
    -------
    tuple[date, date]
        Inclusive start and end dates.

    Raises
    ------
    ValueError
        If *period* is not recognised.
    """
    if period == "Yesterday":
        d = max_date - timedelta(days=1)
        return d, d
    elif period == "WTD":
        # ISO weekday: Monday = 0. Start of week = Monday.
        start = max_date - timedelta(days=max_date.weekday())
        return start, max_date
    elif period == "MTD":
        return max_date.replace(day=1), max_date
    elif period == "QTD":
        return _quarter_start(max_date), max_date
    elif period == "YTD":
        return max_date.replace(month=1, day=1), max_date
    elif period == "Last 7 days":
        return max_date - timedelta(days=6), max_date
    elif period == "Last 30 days":
        return max_date - timedelta(days=29), max_date
    else:
        raise ValueError(
            f"Unknown period '{period}'. "
            f"Expected one of: {', '.join(PERIOD_OPTIONS)}"
        )
