# sections/__init__.py
"""
Dashboard sections — each renders one part of the page.

Import the render functions you need:
    from sections import (
        render_header,
        render_kpi_section,
        render_trend_section,
        render_brand_breakdown,
        render_detail_table,
    )
"""

from sections.header import render_header
from sections.kpi_section import render_kpi_section
from sections.trend_section import render_trend_section
from sections.brand_breakdown import render_brand_breakdown
from sections.detail_table import render_detail_table
from sections.additional_charts import render_additional_charts

__all__ = [
    "render_header",
    "render_kpi_section",
    "render_trend_section",
    "render_brand_breakdown",
    "render_detail_table",
    "render_additional_charts",
]
