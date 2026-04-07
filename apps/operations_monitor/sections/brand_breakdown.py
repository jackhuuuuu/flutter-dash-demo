# sections/brand_breakdown.py
"""
Brand & wallet type breakdown — shows pass/fail distribution by dimension.

Currently only SBT data is available, but this section is built for
multi-brand support. As more brands come online (PPB, FanDuel, etc.),
the charts will automatically show the breakdown.

Also includes a wallet-type breakdown (ALL vs CASH) for the current data.
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.components import section_title, bar_chart
from flutter_dash.components.section_title import multi_section_title
from flutter_dash.helpers import SeriesStyle
from flutter_dash.formatters import fmt_number

from config import (
    COL_BRAND, COL_WALLET_TYPE, COL_OVERALL_STATUS,
    STATUS_PASS, STATUS_FAIL,
)


def _build_breakdown(
    df: pd.DataFrame,
    group_col: str,
    status_col: str = COL_OVERALL_STATUS,
) -> pd.DataFrame:
    """
    Build a pass/fail count breakdown by a grouping dimension.

    Returns a DataFrame with columns: group, pass_count, fail_count.
    """
    grouped = df.groupby(group_col).apply(
        lambda g: pd.Series({
            "pass_count": (g[status_col] == STATUS_PASS).sum(),
            "fail_count": (g[status_col] == STATUS_FAIL).sum(),
        })
    ).reset_index()

    grouped = grouped.rename(columns={group_col: "group"})
    grouped = grouped.sort_values("group")
    return grouped


def render_brand_breakdown(df: pd.DataFrame) -> None:
    """
    Render the brand and wallet type breakdown charts.

    Parameters
    ----------
    df : DataFrame
        Filtered data for the current selections.
    """
    section_title(
        "Breakdown by Dimension",
        "Pass / Fail counts by Brand and Wallet Type",
    )

    if df.empty:
        st.info("No data to display for the selected filters.")
        return

    tokens = get_active_theme()

    styles = [
        SeriesStyle(label="Pass", colour=tokens.positive, dash="solid"),
        SeriesStyle(label="Fail", colour=tokens.negative, dash="solid"),
    ]

    # ── Side-by-side charts ───────────────────────────────────────────────
    multi_section_title([
        ("By Brand", ""),
        ("By Wallet Type", ""),
    ])

    col_left, col_right = st.columns(2)

    # ── Brand breakdown ───────────────────────────────────────────────────
    with col_left:
        brand_df = _build_breakdown(df, COL_BRAND)

        if len(brand_df) > 0:
            fig_brand = bar_chart(
                df=brand_df,
                x_col="group",
                y_cols=["pass_count", "fail_count"],
                series_styles=styles,
                formatter=fmt_number,
                title="",
                height=350,
                barmode="group",
            )
            st.plotly_chart(fig_brand, use_container_width=True, key="breakdown_brand")
        else:
            st.info("No brand data available.")

    # ── Wallet Type breakdown ─────────────────────────────────────────────
    with col_right:
        wallet_df = _build_breakdown(df, COL_WALLET_TYPE)

        if len(wallet_df) > 0:
            fig_wallet = bar_chart(
                df=wallet_df,
                x_col="group",
                y_cols=["pass_count", "fail_count"],
                series_styles=styles,
                formatter=fmt_number,
                title="",
                height=350,
                barmode="group",
            )
            st.plotly_chart(fig_wallet, use_container_width=True, key="breakdown_wallet")
        else:
            st.info("No wallet type data available.")
