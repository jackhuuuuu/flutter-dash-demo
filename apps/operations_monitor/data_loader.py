# apps/operations_monitor/data_loader.py
"""
Data loading for the Operations Monitor dashboard.

Uses the flutter_dash data layer to load from CSV (local dev) or
Databricks Unity Catalog (production).  Change DATA_SOURCE to switch.

The source data comes from the DQ monitor view:
    sandbox_global_finance.jackhu.global_vw_dq_monitor

In local development we read from the sample CSV file instead.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from flutter_dash.data.loader import get_loader

# ── Configuration ─────────────────────────────────────────────────────────────
# Change these when moving to Databricks Apps:
#   DATA_SOURCE = "databricks"
#   LOADER_KWARGS = {
#       "catalog": "sandbox_global_finance",
#       "schema": "jackhu",
#       "table": "global_vw_dq_monitor",
#   }

_DIR = Path(__file__).parent

DATA_SOURCE = "csv"
LOADER_KWARGS = {"file_path": _DIR / "checks_log_sample.csv"}


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the DQ monitor dataset.

    Uses ``@st.cache_data`` so the data is loaded once and cached
    across Streamlit reruns.

    Post-processing:
      - Converts reporting_date to Python date objects
      - Replaces 'null' strings with proper NaN values
      - Converts resolution minutes to numeric
    """
    loader = get_loader(DATA_SOURCE, **LOADER_KWARGS)
    df = loader.load()

    # ── Clean up null strings from CSV export ─────────────────────────────
    # The Databricks CSV export writes literal "null" for missing values.
    df = df.replace("null", pd.NA)

    # ── Ensure date columns are proper date types ─────────────────────────
    if "reporting_date" in df.columns:
        df["reporting_date"] = pd.to_datetime(df["reporting_date"]).dt.date

    if "reporting_month" in df.columns:
        df["reporting_month"] = pd.to_datetime(df["reporting_month"]).dt.date

    # ── Ensure resolution minutes are numeric ─────────────────────────────
    for col in ["revenue_resolution_minutes", "epm_resolution_minutes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
