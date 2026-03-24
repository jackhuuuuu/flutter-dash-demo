# flutter_dash/data/filters.py
"""
Generic DataFrame filtering utilities.

These work with *any* DataFrame — no column names are hardcoded.
Pass the date column name and dimension filters as keyword arguments.

Usage:
    from flutter_dash.data.filters import filter_df, filter_label

    df_filtered = filter_df(
        df,
        date_col="reporting_date",
        start=date(2025, 1, 1),
        end=date(2025, 1, 31),
        brand=["Sky Bet", "PokerStars"],   # dimension_col=allowed_values
        product=["Sports"],
    )

    label = filter_label(selected_brands, all_brands, "Brands")
    # → "All Brands" or "Sky Bet · PokerStars"
"""

from __future__ import annotations

from datetime import date

import pandas as pd


def filter_df(
    df: pd.DataFrame,
    date_col: str,
    start: date,
    end: date,
    **dimension_filters: list,
) -> pd.DataFrame:
    """
    Filter *df* by a date range and zero-or-more dimension columns.

    Parameters
    ----------
    df : DataFrame
        Source data.
    date_col : str
        Name of the column that contains dates.
    start, end : date
        Inclusive date boundaries.
    **dimension_filters
        Each keyword is a column name, each value is a **list** of allowed
        values for that column.  Example: ``brand=["Sky Bet"]``.

    Returns
    -------
    DataFrame
        Filtered copy of *df*.
    """
    mask = (df[date_col] >= start) & (df[date_col] <= end)

    for col_name, allowed_values in dimension_filters.items():
        if allowed_values:  # skip empty lists (= "all")
            mask = mask & df[col_name].isin(allowed_values)

    return df.loc[mask].copy()


def filter_label(
    selected: list,
    all_items: list,
    plural: str,
) -> str:
    """
    Return a concise display label for a filter selection.

    If all items are selected → ``"All {plural}"``
    Otherwise → items joined by `` · ``.

    Examples
    --------
    >>> filter_label(["Sky Bet"], ["Sky Bet", "Paddy Power"], "Brands")
    'Sky Bet'
    >>> filter_label(["Sky Bet", "Paddy Power"], ["Sky Bet", "Paddy Power"], "Brands")
    'All Brands'
    """
    if set(selected) == set(all_items):
        return f"All {plural}"
    return " · ".join(str(v) for v in selected)
