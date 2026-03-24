# flutter_dash/integrations/__init__.py
"""
External service integrations.

Modules:
  - databricks  — Unity Catalog and SQL connector
  - genie       — Genie AI chat and stored answers
"""

from flutter_dash.integrations.databricks import DatabricksConnector
from flutter_dash.integrations.genie import GenieClient

__all__ = [
    "DatabricksConnector",
    "GenieClient",
]
