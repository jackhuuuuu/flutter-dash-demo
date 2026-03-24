# flutter_dash/data/loader.py
"""
Data source abstraction — load data from CSV files or Databricks.

This module provides a simple protocol (interface) for loading data so your
dashboard code doesn't need to know *where* the data comes from.

Classes
-------
- **CsvLoader**         — loads from a local CSV file (good for development).
- **DatabricksLoader**  — loads from Databricks Unity Catalog (for production).
- **get_loader()**      — factory that returns the right loader based on config.

Usage (dashboard code):
    from flutter_dash.data.loader import get_loader

    loader = get_loader(source="csv", file_path="sample_data.csv")
    df = loader.load()

When you deploy to Databricks Apps, just switch the config:
    loader = get_loader(
        source="databricks",
        catalog="flutter_analytics",
        schema="gold",
        table="daily_performance",
    )
    df = loader.load()
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# 1. ABSTRACT BASE — defines the "contract" every loader must follow
# ═════════════════════════════════════════════════════════════════════════════

class DataLoader(ABC):
    """
    Base class for all data loaders.

    Every loader must implement :meth:`load` which returns a
    :class:`~pandas.DataFrame`.
    """

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Load and return the dataset as a DataFrame."""
        ...


# ═════════════════════════════════════════════════════════════════════════════
# 2. CSV LOADER — for local development
# ═════════════════════════════════════════════════════════════════════════════

class CsvLoader(DataLoader):
    """
    Load data from a local CSV file.

    Parameters
    ----------
    file_path : str or Path
        Path to the CSV file.
    date_columns : list[str], optional
        Column names to parse as dates.  Defaults to ``["reporting_date"]``.

    Example
    -------
    loader = CsvLoader("sample_data.csv")
    df = loader.load()
    """

    def __init__(
        self,
        file_path: str | Path,
        date_columns: list[str] | None = None,
    ):
        self.file_path = Path(file_path)
        self.date_columns = date_columns or ["reporting_date"]

    def load(self) -> pd.DataFrame:
        """Read the CSV and convert date columns to ``date`` objects."""
        df = pd.read_csv(self.file_path, parse_dates=self.date_columns)
        # Normalise date columns to Python date objects (not Timestamps)
        for col in self.date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.date
        return df


# ═════════════════════════════════════════════════════════════════════════════
# 3. DATABRICKS LOADER — stub for future Unity Catalog integration
# ═════════════════════════════════════════════════════════════════════════════

class DatabricksLoader(DataLoader):
    """
    Load data from Databricks Unity Catalog via SQL.

    .. note::
        This is a **stub** — the actual Databricks SQL connector will be
        wired in Phase 4 (``flutter_dash.integrations.databricks``).
        For now it raises ``NotImplementedError`` with a helpful message.

    Parameters
    ----------
    catalog : str
        Unity Catalog catalog name, e.g. ``"flutter_analytics"``.
    schema : str
        Schema (database) name, e.g. ``"gold"``.
    table : str
        Table or view name, e.g. ``"daily_performance"``.
    query : str, optional
        Custom SQL query.  If provided, *catalog*/*schema*/*table* are
        ignored and the query is executed directly.
    """

    def __init__(
        self,
        catalog: str = "",
        schema: str = "",
        table: str = "",
        query: str | None = None,
    ):
        self.catalog = catalog
        self.schema = schema
        self.table = table
        self.query = query

    def load(self) -> pd.DataFrame:
        """
        Execute the SQL query and return results as a DataFrame.

        Currently raises ``NotImplementedError`` — will be connected
        in Phase 4 when ``DatabricksConnector`` is implemented.
        """
        raise NotImplementedError(
            "DatabricksLoader will be connected in Phase 4.  "
            "Use CsvLoader for local development."
        )


# ═════════════════════════════════════════════════════════════════════════════
# 4. FACTORY — pick the right loader from config
# ═════════════════════════════════════════════════════════════════════════════

def get_loader(source: str = "csv", **kwargs) -> DataLoader:
    """
    Return the appropriate loader based on *source*.

    Parameters
    ----------
    source : str
        ``"csv"`` or ``"databricks"``.
    **kwargs
        Passed to the loader constructor.  For CSV, expects ``file_path``.
        For Databricks, expects ``catalog``, ``schema``, ``table`` or ``query``.

    Returns
    -------
    DataLoader
        An instance of the matching loader.

    Raises
    ------
    ValueError
        If *source* is not recognised.

    Example
    -------
    loader = get_loader("csv", file_path="sample_data.csv")
    df = loader.load()
    """
    if source == "csv":
        return CsvLoader(**kwargs)
    elif source == "databricks":
        return DatabricksLoader(**kwargs)
    else:
        raise ValueError(
            f"Unknown data source '{source}'. Expected 'csv' or 'databricks'."
        )
