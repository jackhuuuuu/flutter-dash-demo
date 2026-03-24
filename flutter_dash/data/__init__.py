# flutter_dash/data/__init__.py
"""
Data utilities — filtering, aggregation, date helpers, data loaders.

Modules:
  - date_helpers  — period date calculations
  - filters       — generic DataFrame filtering
  - aggregation   — metric aggregation and weighted averages
  - loader        — CSV and Databricks data sources
"""

from flutter_dash.data.date_helpers import get_period_dates, PERIOD_OPTIONS
from flutter_dash.data.filters import filter_df, filter_label
from flutter_dash.data.aggregation import (
    weighted_average,
    aggregate_metric_single,
    aggregate_metrics,
    get_drivers_daily,
    daily_weighted_average,
)
from flutter_dash.data.loader import get_loader, CsvLoader, DatabricksLoader, DataLoader

__all__ = [
    # date_helpers
    "get_period_dates",
    "PERIOD_OPTIONS",
    # filters
    "filter_df",
    "filter_label",
    # aggregation
    "weighted_average",
    "aggregate_metric_single",
    "aggregate_metrics",
    "get_drivers_daily",
    "daily_weighted_average",
    # loader
    "get_loader",
    "CsvLoader",
    "DatabricksLoader",
    "DataLoader",
]
