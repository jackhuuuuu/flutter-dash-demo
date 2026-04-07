---
description: "Add a new chart type to flutter_dash/components/charts.py and export it"
---
Add a new chart type called "${input:chartName}" to `flutter_dash/components/charts.py`.

Requirements:
- Follow the same pattern as existing charts (line_chart, bar_chart, heatmap_chart)
- Accept optional `tokens: ThemeTokens` parameter, default to `get_active_theme()`
- Use `base_layout(tokens)` for the Plotly layout
- Include a full docstring with Parameters, Returns, and Examples sections
- Export from `flutter_dash/components/__init__.py`
- Update `README.md` and `CHANGELOG.md`

The chart should: ${input:chartDescription}
