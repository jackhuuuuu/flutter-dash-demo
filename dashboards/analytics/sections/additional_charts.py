# dashboards/analytics/sections/additional_charts.py
"""
Additional chart examples — pie and waterfall charts.

Demonstrates other chart types available in the flutter_dash framework
using the same sample data.
"""

import streamlit as st
import pandas as pd

from flutter_dash.components import pie_chart, waterfall_chart, section_title
from flutter_dash.formatters import fmt_currency

from dashboards.analytics.config import METRIC_DRIVERS


def render_additional_charts(
    df_period: pd.DataFrame,
    period: str,
    brand_label: str,
    product_label: str,
) -> None:
    """
    Render additional chart examples beneath the main dashboard sections.

    Includes:
      1. Revenue Mix by Product (donut chart)
      2. Net Revenue Bridge — LY to TY (waterfall chart)
    """
    if df_period.empty:
        return

    # ── 1. Revenue Mix Donut ──────────────────────────────────────────────────
    section_title(
        "Revenue Mix by Product",
        f"{period} · {brand_label} · {product_label} · TY Net Revenue composition",
    )

    product_revenue = (
        df_period
        .groupby("product")["total_net_revenue"]
        .sum()
        .reset_index()
        .sort_values("total_net_revenue", ascending=False)
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        fig_pie = pie_chart(
            df=product_revenue,
            label_col="product",
            value_col="total_net_revenue",
            formatter=fmt_currency,
            title=f"Net Revenue Share by Product ({period})",
            height=400,
            hole=0.45,
        )
        st.plotly_chart(fig_pie, width="stretch")

    # ── 2. Revenue Bridge (Waterfall) ─────────────────────────────────────────
    with col2:
        # Build bridge: LY Total → driver effects → TY Total
        ly_total = df_period["total_net_revenue_ly"].sum()
        ty_total = df_period["total_net_revenue"].sum()

        driver_cols = METRIC_DRIVERS.get("Net Revenue", [])
        categories = ["LY Revenue"]
        values = [ly_total]

        for d_col in driver_cols:
            if d_col in df_period.columns:
                d_label = d_col.replace("_", " ").title()
                d_val = df_period[d_col].sum()
                categories.append(d_label)
                values.append(d_val)

        categories.append("TY Revenue")
        values.append(ty_total)

        fig_wf = waterfall_chart(
            categories=categories,
            values=values,
            formatter=fmt_currency,
            title=f"Net Revenue Bridge — LY to TY ({period})",
            height=400,
        )
        st.plotly_chart(fig_wf, width="stretch")
