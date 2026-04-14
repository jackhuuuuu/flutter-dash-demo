# apps/operations_monitor/config.py
"""
Configuration for the Operations Monitor dashboard.

This file contains all dashboard-specific settings:
  - Page config (title, icon)
  - Data source paths
  - Column name mappings for file delivery, check-level, and mapping tables
  - Status values and lifecycle labels
  - Sidebar filter dimensions

The Operations Monitor tracks data quality (DQ) check results and
file delivery status.  It is designed for multi-brand support and
operational visibility for both technical and non-technical users.
"""

# ── Page settings ─────────────────────────────────────────────────────────────
PAGE_TITLE = "Operations Monitor"
PAGE_ICON = "🔧"
DASHBOARD_HEADING = "Operations Monitor"
DASHBOARD_SUBTITLE = "File Delivery Status | Data Quality Checks"

# ── Data source ───────────────────────────────────────────────────────────────
DATA_SOURCE = "csv"

CSV_FILE_DELIVERY = "global_vw_file_delivery_sample_v2.csv"
CSV_DQ_MONITOR = "global_vw_dq_monitor_sample_v2.csv"
CSV_CHECK_FILE_MAPPING = "global_dq_check_file_mapping.csv"

# ── Shared column names ──────────────────────────────────────────────────────
COL_REPORTING_MONTH = "reporting_month"
COL_REPORTING_DATE = "reporting_date"
COL_BRAND = "brand"

# ── File delivery view columns ───────────────────────────────────────────────
COL_FILE_NAME = "file_name"
COL_CURRENT_FLAG = "current_flag"
COL_FILE_ERP_STATUS = "erp_status"
COL_FILE_EPM_STATUS = "epm_status"
COL_FILE_OVERALL_STATUS = "overall_status"
COL_EPM_DELIVERED_AT = "epm_delivered_at"
COL_ERP_FIRST_DELIVERED_AT = "erp_first_delivered_at"
COL_ERP_FINAL_DELIVERED_AT = "erp_final_delivered_at"
COL_ERP_FINAL_RESENT_AT = "erp_final_resent_at"
COL_FILE_LATEST_RUN = "latest_run_timestamp"
COL_LATEST_ROW_COUNT = "latest_row_count"
COL_EPM_DELIVERY_DAYS = "epm_delivery_days"
COL_ERP_DELIVERY_DAYS = "erp_delivery_days"
COL_ERP_RESOLUTION_HRS = "erp_resolution_hours"
COL_DELIVERY_LIFECYCLE = "delivery_lifecycle"

# ── DQ monitor (check-level) view columns ────────────────────────────────────
COL_WALLET_TYPE = "wallet_type"
COL_CHECK_NAME = "check_name"
COL_CHECK_DAILY_VALUE = "check_daily_value"
COL_CHECK_MTD_VALUE = "check_mtd_value"
COL_DAILY_REV_TOLERANCE = "daily_revenue_tolerance"
COL_MTD_REV_TOLERANCE = "mtd_revenue_tolerance"
COL_DAILY_EPM_TOLERANCE = "daily_epm_tolerance"
COL_MTD_EPM_TOLERANCE = "mtd_epm_tolerance"
COL_REVENUE_STATUS = "revenue_status"
COL_EPM_STATUS = "epm_status"
COL_OVERALL_STATUS = "overall_status"
COL_CHECK_LATEST_RUN = "latest_run_timestamp"

# Check-level failure lifecycle columns
COL_REV_FIRST_FAILED = "revenue_first_failed_at"
COL_REV_RESOLVED = "revenue_resolved_at"
COL_REV_LIFECYCLE = "revenue_failure_lifecycle"
COL_REV_RESOLUTION_HRS = "revenue_resolution_hours"
COL_EPM_FIRST_FAILED = "epm_first_failed_at"
COL_EPM_RESOLVED = "epm_resolved_at"
COL_EPM_LIFECYCLE = "epm_failure_lifecycle"
COL_EPM_RESOLUTION_HRS = "epm_resolution_hours"

# ── Check-to-file mapping columns ────────────────────────────────────────────
COL_MAP_CHECK_NAME = "check_name"
COL_MAP_FILE_NAME = "file_name"
COL_MAP_BRAND = "brand"
COL_MAP_STATUS = "request_status"
COL_MAP_EFFECTIVE_FROM = "effective_from"
COL_MAP_EFFECTIVE_TO = "effective_to"

# ── Status / lifecycle constants ──────────────────────────────────────────────
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"

LIFECYCLE_NEVER_FAILED = "NEVER_FAILED"
LIFECYCLE_RESOLVED = "RESOLVED"
LIFECYCLE_UNRESOLVED = "UNRESOLVED"

DELIVERY_ERP_DELIVERED = "ERP_DELIVERED"
DELIVERY_EPM_ONLY = "EPM_ONLY"
DELIVERY_MANUAL_OVERRIDE = "MANUAL_OVERRIDE"

# ── Sidebar filter dimensions ────────────────────────────────────────────────
DIMENSIONS: dict[str, str] = {
    COL_BRAND: "Brand",
}

# ── Status type toggles ──────────────────────────────────────────────────────
# File delivery tab
FILE_STATUS_TYPES = {
    "Overall": COL_FILE_OVERALL_STATUS,
    "ERP": COL_FILE_ERP_STATUS,
    "EPM": COL_FILE_EPM_STATUS,
}

# Check detail tab
CHECK_STATUS_TYPES = {
    "Overall": COL_OVERALL_STATUS,
    "Revenue": COL_REVENUE_STATUS,
    "EPM": COL_EPM_STATUS,
}
