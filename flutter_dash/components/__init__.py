# flutter_dash/components/__init__.py
"""
Reusable UI components for Streamlit dashboards.

Import any component directly:
    from flutter_dash.components import kpi_card, line_chart, bar_chart
    from flutter_dash.components import pie_chart, waterfall_chart
    from flutter_dash.components import section_title, data_table
    from flutter_dash.components import SidebarBuilder
"""

from flutter_dash.components.kpi_card import kpi_card          # noqa: F401
from flutter_dash.components.section_title import section_title, multi_section_title  # noqa: F401
from flutter_dash.components.charts import (                    # noqa: F401
    line_chart,
    bar_chart,
    pie_chart,
    waterfall_chart,
)
from flutter_dash.components.data_table import data_table       # noqa: F401
from flutter_dash.components.sidebar import SidebarBuilder      # noqa: F401
