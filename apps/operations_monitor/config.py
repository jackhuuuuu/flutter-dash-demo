# apps/operations_monitor/config.py
"""
Configuration for the Operations Monitor dashboard.

This file contains all dashboard-specific settings:
  - Page config (title, icon)
  - Column name mappings (so section code reads clearly)
  - Status colour mapping
  - Filter dimensions

The Operations Monitor tracks data quality (DQ) check results and,
in future, Databricks job/pipeline performance.  It is designed for
multi-brand support and operational visibility for both technical
and non-technical users.
"""

# ── Page settings ─────────────────────────────────────────────────────────────
PAGE_TITLE = "Operations Monitor"
PAGE_ICON = "🔧"
DASHBOARD_HEADING = "Operations Monitor"
DASHBOARD_SUBTITLE = "Data Quality Checks | Pipeline Health"

# ── Column names in the source data ──────────────────────────────────────────
# Keeping these in one place means if the Databricks view columns change,
# you only update here — not in every section file.

COL_REPORTING_MONTH = "reporting_month"
COL_REPORTING_DATE = "reporting_date"
COL_BRAND = "brand"
COL_WALLET_TYPE = "wallet_type"
COL_CHECK_NAME = "check_name"
COL_REVENUE_STATUS = "revenue_status"
COL_EPM_STATUS = "epm_status"
COL_OVERALL_STATUS = "overall_status"
COL_LATEST_RUN = "latest_run_timestamp"

# Failure lifecycle columns
COL_REV_FIRST_FAILED = "revenue_first_failed_at"
COL_REV_RESOLVED = "revenue_resolved_at"
COL_REV_LIFECYCLE = "revenue_failure_lifecycle"
COL_REV_RESOLUTION_MINS = "revenue_resolution_minutes"

COL_EPM_FIRST_FAILED = "epm_first_failed_at"
COL_EPM_RESOLVED = "epm_resolved_at"
COL_EPM_LIFECYCLE = "epm_failure_lifecycle"
COL_EPM_RESOLUTION_MINS = "epm_resolution_minutes"

# ── Status values ─────────────────────────────────────────────────────────────
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"

LIFECYCLE_NEVER_FAILED = "NEVER_FAILED"
LIFECYCLE_RESOLVED = "RESOLVED"
LIFECYCLE_UNRESOLVED = "UNRESOLVED"

# ── Sidebar filter dimensions ────────────────────────────────────────────────
# Maps column name → display label for sidebar filters.
DIMENSIONS: dict[str, str] = {
    COL_BRAND: "Brand",
    COL_WALLET_TYPE: "Wallet Type",
}

# ── Status type options (for toggling between Revenue / EPM / Overall) ───────
STATUS_TYPES = {
    "Overall": COL_OVERALL_STATUS,
    "Revenue": COL_REVENUE_STATUS,
    "EPM": COL_EPM_STATUS,
}
