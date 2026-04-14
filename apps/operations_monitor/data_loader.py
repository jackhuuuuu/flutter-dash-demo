# apps/operations_monitor/data_loader.py
"""
Data loading for the Operations Monitor dashboard.

Loads three datasets:
  - File delivery status  (global_vw_file_delivery)
  - DQ check results      (global_vw_dq_monitor)
  - Check-to-file mapping (global_dq_check_file_mapping)

CSV for local dev, Databricks for production.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

import config

_DIR = Path(__file__).parent


@st.cache_data
def load_file_delivery() -> pd.DataFrame:
    """Load the file delivery dataset."""
    df = pd.read_csv(_DIR / config.CSV_FILE_DELIVERY)
    df = df.replace("null", pd.NA)
    df[config.COL_REPORTING_DATE] = pd.to_datetime(df[config.COL_REPORTING_DATE])
    df[config.COL_REPORTING_MONTH] = pd.to_datetime(df[config.COL_REPORTING_MONTH])
    for col in [config.COL_ERP_DELIVERY_DAYS, config.COL_EPM_DELIVERY_DAYS,
                config.COL_ERP_RESOLUTION_HRS, config.COL_LATEST_ROW_COUNT]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_dq_monitor() -> pd.DataFrame:
    """Load the DQ check-level dataset."""
    df = pd.read_csv(_DIR / config.CSV_DQ_MONITOR)
    df = df.replace("null", pd.NA)
    df[config.COL_REPORTING_DATE] = pd.to_datetime(df[config.COL_REPORTING_DATE])
    df[config.COL_REPORTING_MONTH] = pd.to_datetime(df[config.COL_REPORTING_MONTH])
    for col in [config.COL_REV_RESOLUTION_HRS, config.COL_EPM_RESOLUTION_HRS,
                config.COL_CHECK_DAILY_VALUE, config.COL_CHECK_MTD_VALUE,
                config.COL_DAILY_REV_TOLERANCE, config.COL_MTD_REV_TOLERANCE,
                config.COL_DAILY_EPM_TOLERANCE, config.COL_MTD_EPM_TOLERANCE]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_check_file_mapping() -> pd.DataFrame:
    """Load the check-to-file mapping table (small, static metadata)."""
    df = pd.read_csv(_DIR / config.CSV_CHECK_FILE_MAPPING)
    df = df.replace("null", pd.NA)
    df = df[df[config.COL_MAP_STATUS] == "APPROVED"]
    return df
