# flutter_dash/integrations/databricks.py
"""
Databricks Unity Catalog connector.

Provides a single class — :class:`DatabricksConnector` — that wraps the
``databricks-sql-connector`` library to run SQL queries against Unity
Catalog tables and return Pandas DataFrames.

Authentication
--------------
When running inside **Databricks Apps**, authentication is automatic
(uses the app's service principal via environment variables).

For **local development**, you can either:
  1. Set the env vars ``DATABRICKS_HOST`` and ``DATABRICKS_TOKEN``
  2. Or pass ``host`` and ``token`` explicitly to the constructor.

If the connector library is not installed or credentials are missing,
the class falls back gracefully: :meth:`is_available` returns ``False``
and :meth:`query` / :meth:`read_table` raise ``RuntimeError`` with
a clear message.

Usage:
    from flutter_dash.integrations.databricks import DatabricksConnector

    db = DatabricksConnector()
    if db.is_available():
        df = db.read_table("flutter_analytics", "gold", "daily_performance")
    else:
        print("Databricks not configured — using CSV fallback")
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Try to import the Databricks SQL connector.
# It's an optional dependency — won't be installed during local CSV dev.
try:
    from databricks import sql as databricks_sql  # type: ignore[import-untyped]

    _HAS_CONNECTOR = True
except ImportError:
    _HAS_CONNECTOR = False


class DatabricksConnector:
    """
    Connect to Databricks Unity Catalog and run SQL queries.

    Parameters
    ----------
    host : str, optional
        Databricks workspace URL (e.g. ``"adb-1234567890.1.azuredatabricks.net"``).
        Falls back to ``DATABRICKS_HOST`` env var.
    token : str, optional
        Personal access token or service principal token.
        Falls back to ``DATABRICKS_TOKEN`` env var.
    http_path : str, optional
        SQL warehouse HTTP path.
        Falls back to ``DATABRICKS_HTTP_PATH`` env var.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        http_path: Optional[str] = None,
    ):
        self.host = host or os.environ.get("DATABRICKS_HOST", "")
        self.token = token or os.environ.get("DATABRICKS_TOKEN", "")
        self.http_path = http_path or os.environ.get("DATABRICKS_HTTP_PATH", "")

    # ── Public helpers ────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """
        Return ``True`` if the connector library is installed **and**
        credentials are configured.
        """
        return (
            _HAS_CONNECTOR
            and bool(self.host)
            and bool(self.token)
            and bool(self.http_path)
        )

    # ── Core query method ─────────────────────────────────────────────────

    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL statement and return the results as a DataFrame.

        Parameters
        ----------
        sql : str
            A read-only SQL query (SELECT).

        Returns
        -------
        DataFrame
            Query results.

        Raises
        ------
        RuntimeError
            If the connector is not available (library or credentials missing).
        """
        if not _HAS_CONNECTOR:
            raise RuntimeError(
                "databricks-sql-connector is not installed.  "
                "Install it with:  pip install databricks-sql-connector"
            )
        if not self.is_available():
            raise RuntimeError(
                "Databricks credentials not configured.  "
                "Set DATABRICKS_HOST, DATABRICKS_TOKEN, and "
                "DATABRICKS_HTTP_PATH environment variables, or pass them "
                "to DatabricksConnector()."
            )

        logger.info("Executing Databricks SQL query (%d chars)", len(sql))
        with databricks_sql.connect(
            server_hostname=self.host,
            http_path=self.http_path,
            access_token=self.token,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=columns)

    # ── Convenience wrapper ───────────────────────────────────────────────

    def read_table(
        self,
        catalog: str,
        schema: str,
        table: str,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Read an entire Unity Catalog table into a DataFrame.

        Parameters
        ----------
        catalog : str
            Catalog name, e.g. ``"flutter_analytics"``.
        schema : str
            Schema name, e.g. ``"gold"``.
        table : str
            Table or view name, e.g. ``"daily_performance"``.
        limit : int, optional
            Maximum number of rows to fetch.  ``None`` = all rows.

        Returns
        -------
        DataFrame
        """
        # Use backtick quoting for catalog/schema/table identifiers
        fqn = f"`{catalog}`.`{schema}`.`{table}`"
        sql = f"SELECT * FROM {fqn}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return self.query(sql)
