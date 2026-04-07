# sections/__init__.py
"""
Operations Monitor sections — each renders one part of the dashboard.

Import the render functions you need:
    from sections import (
        render_header,
        render_kpi_section,
        render_heatmap,
        render_trend_section,
        render_lifecycle_section,
        render_resolution_section,
        render_detail_table,
        render_brand_breakdown,
    )
"""

from sections.header import render_header
from sections.kpi_section import render_kpi_section
from sections.heatmap import render_heatmap
from sections.trend_section import render_trend_section
from sections.lifecycle_section import render_lifecycle_section
from sections.resolution_section import render_resolution_section
from sections.detail_table import render_detail_table
from sections.brand_breakdown import render_brand_breakdown

__all__ = [
    "render_header",
    "render_kpi_section",
    "render_heatmap",
    "render_trend_section",
    "render_lifecycle_section",
    "render_resolution_section",
    "render_detail_table",
    "render_brand_breakdown",
]
