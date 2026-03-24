# dashboards/analytics/data_loader.py
"""
Data loading for the Flutter Analytics dashboard.

Uses the flutter_dash data layer to load from CSV (local dev) or
Databricks Unity Catalog (production).  Change DATA_SOURCE to switch.
"""

import streamlit as st
import pandas as pd

from flutter_dash.data.loader import get_loader

# ── Configuration ─────────────────────────────────────────────────────────────
# Change these when moving to Databricks Apps:
#   DATA_SOURCE = "databricks"
#   LOADER_KWARGS = {"catalog": "flutter_analytics", "schema": "gold", "table": "daily_performance"}

DATA_SOURCE = "csv"
LOADER_KWARGS = {"file_path": "sample_data.csv"}


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the analytics dataset.

    Uses ``@st.cache_data`` so the data is loaded once and cached
    across Streamlit reruns.  Change DATA_SOURCE above to switch
    between CSV and Databricks.
    """
    loader = get_loader(DATA_SOURCE, **LOADER_KWARGS)
    return loader.load()
