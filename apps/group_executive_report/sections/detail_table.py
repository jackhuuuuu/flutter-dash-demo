# sections/detail_table.py
"""
Detailed breakdown table section — Brand → Product hierarchy.
"""

import streamlit as st
import pandas as pd

from flutter_dash.components import data_table, section_title

from config import TABLE_METRICS, TABLE_GROUP_BY


def render_detail_table(
    df_period: pd.DataFrame,
    period: str,
    brand_label: str,
    product_label: str,
) -> None:
    """
    Render the detailed breakdown table with brand/product hierarchy.

    Parameters
    ----------
    df_period : DataFrame
        Filtered data for the selected period.
    period, brand_label, product_label : str
        Display labels.
    """
    section_title(
        "Detailed Breakdown",
        f"{period} · {brand_label} · {product_label} · Brand / Product grain",
    )

    if df_period.empty:
        st.info("No data available for the selected period and filters.")
        return

    data_table(
        df=df_period,
        metrics=TABLE_METRICS,
        group_by=TABLE_GROUP_BY,
        currency_unit="thousands",
    )
