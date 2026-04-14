# sections/__init__.py
"""
Operations Monitor sections — each renders one part of the dashboard.

Organised into two tabs:
  - File Delivery: file_kpi_section, file_heatmap, file_detail_table
  - Check Detail:  kpi_section, heatmap, detail_table
"""

# Shared
from sections.header import render_header

# File delivery tab
from sections.file_kpi_section import render_file_kpi_section
from sections.file_heatmap import render_file_heatmap
from sections.file_detail_table import render_file_detail_table

# Check detail tab
from sections.kpi_section import render_kpi_section
from sections.heatmap import render_heatmap
from sections.detail_table import render_detail_table

__all__ = [
    "render_header",
    # File delivery
    "render_file_kpi_section",
    "render_file_heatmap",
    "render_file_detail_table",
    # Check detail
    "render_kpi_section",
    "render_heatmap",
    "render_detail_table",
]
