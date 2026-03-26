# hub/hub_config.py
"""
FBI Hub — App Registry.

This is the central registry for all apps shown on the FBI Hub.
To add a new dashboard or app, simply add an entry to the appropriate
section list below.

Each entry is a dict with:
  - id          : unique slug (used for HTML element IDs)
  - title       : display name on the tile
  - description : short description (1-2 sentences)
  - icon        : emoji icon for the tile
  - status      : "live" or "coming_soon"
  - local_port  : port for local development (streamlit run --server.port)
  - app_path    : relative path from repo root (for Databricks deployment YAML)
  - internal    : True if the app uses flutter_dash theming (theme param passed)
  - url         : (optional) full URL override for external apps
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION DEFINITIONS
# Each section groups related apps together on the hub page.
# ─────────────────────────────────────────────────────────────────────────────

SECTIONS = [
    {
        "id": "dashboards",
        "title": "Dashboards",
        "subtitle": "Interactive reporting dashboards for finance and performance analysis.",
        "icon": "📊",
    },
    {
        "id": "ai_apps",
        "title": "AI & Analytics Apps",
        "subtitle": "AI-infused tools and advanced analytics powered by Databricks.",
        "icon": "🤖",
    },
    {
        "id": "external",
        "title": "External Tools & Collaboration",
        "subtitle": "Third-party tools and cross-team applications.",
        "icon": "🔗",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# APP REGISTRY
# Add new apps here. They will appear in the section matching their "section" key.
# ─────────────────────────────────────────────────────────────────────────────

APPS = [
    # ── Dashboards ────────────────────────────────────────────────────────────
    {
        "id": "group_executive_report",
        "title": "Group Executive Report",
        "description": (
            "Multi-brand, multi-product performance dashboard with KPIs, "
            "daily trends, brand breakdowns, and variance analysis."
        ),
        "icon": "📊",
        "section": "dashboards",
        "status": "live",
        "local_port": 8502,
        "app_path": "apps/group_executive_report",
        "cloud_url": "https://flutter-dash-demo-nip8zbftupozngv5a28zna.streamlit.app",
        "internal": True,
    },
    {
        "id": "pl_dashboard",
        "title": "P&L Dashboard",
        "description": (
            "Profit & Loss reporting with drill-down by cost centre, "
            "entity, and period comparison."
        ),
        "icon": "💰",
        "section": "dashboards",
        "status": "coming_soon",
        "local_port": 8503,
        "app_path": "apps/pl_dashboard",
        "internal": True,
    },
    {
        "id": "trading_dashboard",
        "title": "Trading Dashboard",
        "description": (
            "Real-time trading metrics and event-level performance "
            "across sports and gaming products."
        ),
        "icon": "📈",
        "section": "dashboards",
        "status": "coming_soon",
        "local_port": 8504,
        "app_path": "apps/trading_dashboard",
        "internal": True,
    },

    # ── AI & Analytics Apps ───────────────────────────────────────────────────
    {
        "id": "genie_assistant",
        "title": "Genie Data Assistant",
        "description": (
            "Ask questions in plain English and get instant answers "
            "from your data using Databricks Genie."
        ),
        "icon": "🧞",
        "section": "ai_apps",
        "status": "coming_soon",
        "local_port": 8510,
        "app_path": "apps/genie_assistant",
        "internal": True,
    },
    {
        "id": "anomaly_detector",
        "title": "Anomaly Detection",
        "description": (
            "ML-powered anomaly detection for revenue, stakes, "
            "and margin metrics with automated alerting."
        ),
        "icon": "🔍",
        "section": "ai_apps",
        "status": "coming_soon",
        "local_port": 8511,
        "app_path": "apps/anomaly_detector",
        "internal": True,
    },

    # ── External Tools ────────────────────────────────────────────────────────
    # Example: link to an external tool or another team's app.
    # Set "url" to override the auto-generated link.
    # {
    #     "id": "partner_app",
    #     "title": "Partner Team App",
    #     "description": "An app built by another team.",
    #     "icon": "🌐",
    #     "section": "external",
    #     "status": "live",
    #     "url": "https://partner-team-app.databricks.com",
    #     "internal": False,
    # },
]
