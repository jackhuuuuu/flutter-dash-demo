# flutter_dash/components/charts.py
"""
Chart components — fully dynamic, accept any number of series.

Every chart function follows the same pattern:
  1. Pass your DataFrame + column names
  2. Optionally pass SeriesStyle objects to control colours/dashes
  3. If you don't pass styles, colours are auto-assigned from the theme
  4. Pass a formatter function to control value display (currency, %, number)

This means you can create a line chart with 2 series or 10 series —
it adapts automatically.

Available charts:
  - line_chart()      — multi-series line chart with optional driver tooltips
  - bar_chart()       — grouped or stacked bar chart
  - pie_chart()       — pie/donut chart for composition analysis
  - waterfall_chart()  — bridge chart for variance/driver analysis
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Callable, List, Optional

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import ThemeTokens
from flutter_dash.theme.plotly import base_layout
from flutter_dash.formatters import fmt_currency, fmt_pct
from flutter_dash.helpers import SeriesStyle


# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL: Auto-generate series styles from theme when not provided
# ═════════════════════════════════════════════════════════════════════════════

# Default dash patterns — cycles through these for many series
_DASH_CYCLE = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]


def _fill_colours(
    styles: List[SeriesStyle],
    tokens: ThemeTokens,
) -> List[SeriesStyle]:
    """
    Fill in empty colour fields on SeriesStyle objects using the theme palette.

    This lets callers create ``SeriesStyle(label="TY", dash="solid")`` without
    specifying a colour — the colour is assigned from the theme automatically.
    """
    colours = tokens.chart_series
    result = []
    for i, s in enumerate(styles):
        if s.colour:
            result.append(s)
        else:
            result.append(SeriesStyle(
                label=s.label,
                colour=colours[i % len(colours)],
                dash=s.dash,
            ))
    return result


def _auto_styles(
    labels: List[str],
    tokens: ThemeTokens,
) -> List[SeriesStyle]:
    """
    Create SeriesStyle objects automatically from the theme palette.

    Colours come from tokens.chart_series (cycles if more series than colours).
    Dash patterns cycle through solid → dash → dot → ...

    This is called when you don't pass explicit series_styles.
    """
    colours = tokens.chart_series
    styles = []
    for i, label in enumerate(labels):
        styles.append(SeriesStyle(
            label=label,
            colour=colours[i % len(colours)],
            dash=_DASH_CYCLE[i % len(_DASH_CYCLE)],
        ))
    return styles


# ═════════════════════════════════════════════════════════════════════════════
# LINE CHART
# ═════════════════════════════════════════════════════════════════════════════

def line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    series_styles: Optional[List[SeriesStyle]] = None,
    formatter: Callable[[float], str] = fmt_currency,
    title: str = "",
    height: int = 380,
    drivers_df: Optional[pd.DataFrame] = None,
    drivers_formatter: Optional[Callable[[float], str]] = None,
    tokens: Optional[ThemeTokens] = None,
) -> go.Figure:
    """
    Multi-series line chart with rich tooltips.

    Fully dynamic — pass any number of y_cols and they'll each get their
    own coloured line. Tooltips show all series values at each date point.

    Parameters
    ----------
    df : DataFrame
        Data to plot.
    x_col : str
        Column name for the x-axis (typically a date column).
    y_cols : list[str]
        Column names for each series to plot. Can be 1, 3, 5, or any number.
    series_styles : list[SeriesStyle], optional
        Visual style for each series (colour, dash, label).
        If None, auto-generated from the theme palette.
        Must match the length of y_cols if provided.
    formatter : Callable
        How to format y-axis values in tooltips (e.g. fmt_currency, fmt_pct).
    title : str
        Chart title.
    height : int
        Chart height in pixels. Default 380.
    drivers_df : DataFrame, optional
        A separate DataFrame with driver columns (e.g. volume_effect).
        Must share the same x_col for merging. Driver values appear in tooltips.
    drivers_formatter : Callable, optional
        How to format driver values. Defaults to the main formatter.
    tokens : ThemeTokens, optional
        Theme palette. Defaults to active theme.

    Returns
    -------
    go.Figure
        A Plotly figure ready to pass to st.plotly_chart().

    Examples
    --------
    # Basic 3-series chart (auto-colours):
    fig = line_chart(df, "date", ["revenue_ty", "revenue_ly", "revenue_bud"],
                     formatter=fmt_currency, title="Revenue Trend")

    # 5-series chart with custom styles:
    styles = [
        SeriesStyle("Actual", "#00D4FF", "solid"),
        SeriesStyle("Budget", "#FFB300", "dot"),
        SeriesStyle("Forecast", "#A78BFA", "dash"),
        SeriesStyle("Low", "#34D399", "dashdot"),
        SeriesStyle("High", "#FF6B6B", "dashdot"),
    ]
    fig = line_chart(df, "date", ["actual", "budget", "forecast", "low", "high"],
                     series_styles=styles, formatter=fmt_currency)
    """
    if tokens is None:
        tokens = get_active_theme()
    if drivers_formatter is None:
        drivers_formatter = formatter

    # Auto-generate styles if not provided, or fill in missing colours
    labels = [s.label for s in series_styles] if series_styles else y_cols
    if series_styles is None:
        series_styles = _auto_styles(labels, tokens)
    else:
        series_styles = _fill_colours(series_styles, tokens)

    # Build layout
    layout = base_layout(tokens, height=height)
    layout["title"] = dict(
        text=title,
        font=dict(size=13, color=tokens.text_muted),
        x=0.01,
    )

    fig = go.Figure()
    n = len(df)

    # ── Pre-format all series values for tooltips ─────────────────────────────
    all_formatted = {}
    for col, style in zip(y_cols, series_styles):
        if col not in df.columns:
            all_formatted[style.label] = ["N/A"] * n
        else:
            all_formatted[style.label] = [formatter(v) for v in df[col]]

    # ── Pre-format drivers if provided ────────────────────────────────────────
    has_drivers = drivers_df is not None and not drivers_df.empty
    driver_cols_present = []
    driver_fmt = {}

    if has_drivers:
        driver_cols_present = [c for c in drivers_df.columns if c != x_col]

        # Merge drivers onto the main data by x_col
        drivers_merged = df.copy()
        drivers_merged[x_col] = pd.to_datetime(drivers_merged[x_col])
        d_copy = drivers_df.copy()
        d_copy[x_col] = pd.to_datetime(d_copy[x_col])
        drivers_merged = drivers_merged.merge(d_copy, on=x_col, how="left")

        for d_col in driver_cols_present:
            driver_fmt[d_col] = [
                drivers_formatter(v) if pd.notna(v) else "N/A"
                for v in drivers_merged[d_col]
            ]

    # ── Build one trace per series ────────────────────────────────────────────
    for col, style in zip(y_cols, series_styles):
        if col not in df.columns:
            continue
        i_col = y_cols.index(col)

        # Build custom data array for tooltips
        # Each row: [formatted value for each series..., then each driver...]
        custom = []
        for i in range(n):
            row = [all_formatted[s.label][i] for s in series_styles]
            if has_drivers:
                row += [driver_fmt[dc][i] for dc in driver_cols_present]
            custom.append(row)

        # Build hover template — shows ALL series on every tooltip
        hover_lines = ["<b>%{x|%d %b %Y}</b><br><br>"]
        for i_s, s in enumerate(series_styles):
            # ● for the hovered series, ○ for others
            marker = "●" if s.label == style.label else "○"
            hover_lines.append(
                f"{marker} <b>{s.label}:</b> %{{customdata[{i_s}]}}<br>"
            )

        # Append driver section if available
        if has_drivers:
            base_idx = len(series_styles)
            hover_lines.append(
                "<br><span style='font-size:11px;opacity:.75;'>Drivers \u2014 YoY</span><br>"
            )
            for d_i, d_col in enumerate(driver_cols_present):
                d_label = d_col.replace("_", " ").title()
                hover_lines.append(
                    f"  {d_label}: %{{customdata[{base_idx + d_i}]}}<br>"
                )

        hover_lines.append("<extra></extra>")

        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            name=style.label,
            legendrank=i_col,
            mode="lines+markers",
            line=dict(color=style.colour, width=2.5, dash=style.dash),
            marker=dict(size=4, color=style.colour),
            customdata=custom,
            hovertemplate="".join(hover_lines),
        ))

    fig.update_layout(**layout)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# BAR CHART
# ═════════════════════════════════════════════════════════════════════════════

def bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    series_styles: Optional[List[SeriesStyle]] = None,
    formatter: Callable[[float], str] = fmt_currency,
    title: str = "",
    height: int = 420,
    barmode: str = "group",
    tokens: Optional[ThemeTokens] = None,
) -> go.Figure:
    """
    Grouped or stacked bar chart with value labels on top.

    Fully dynamic — pass any number of y_cols. Each gets its own colour
    either from series_styles or auto-assigned from the theme.

    Parameters
    ----------
    df : DataFrame
        Data to plot.
    x_col : str
        Column for x-axis categories (e.g. brand, product, month).
    y_cols : list[str]
        Column names for each bar group.
    series_styles : list[SeriesStyle], optional
        Visual style for each series. If None, auto-generated from theme.
    formatter : Callable
        How to format bar labels and tooltips.
    title : str
        Chart title.
    height : int
        Chart height in pixels. Default 420.
    barmode : str
        "group" for side-by-side, "stack" for stacked. Default "group".
    tokens : ThemeTokens, optional
        Theme palette. Defaults to active theme.

    Returns
    -------
    go.Figure
    """
    if tokens is None:
        tokens = get_active_theme()

    # Auto-generate styles if not provided, or fill in missing colours
    labels = [s.label for s in series_styles] if series_styles else y_cols
    if series_styles is None:
        series_styles = _auto_styles(labels, tokens)
    else:
        series_styles = _fill_colours(series_styles, tokens)

    layout = base_layout(tokens, height=height)
    layout["title"] = dict(
        text=title,
        font=dict(size=13, color=tokens.text_muted),
        x=0.01,
    )
    layout["barmode"] = barmode
    layout["bargap"] = 0.25
    layout["bargroupgap"] = 0.08

    fig = go.Figure()

    # Sort series by display_order if provided (controls bar position in group)
    indexed_pairs = list(enumerate(zip(y_cols, series_styles)))
    indexed_pairs.sort(key=lambda x: (
        x[1][1].display_order if x[1][1].display_order is not None else x[0]
    ))

    for orig_idx, (col, style) in indexed_pairs:
        if col not in df.columns:
            continue

        # legendrank based on original series order (TY=0, LY=1, Budget=2)
        # so legend always shows TY first regardless of bar display order
        legend_rank = orig_idx

        text_vals = [formatter(v) for v in df[col]]

        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[col],
            name=style.label,
            legendrank=legend_rank,
            marker=dict(
                color=style.colour,
                opacity=0.85,
                line=dict(color=style.colour, width=0),
            ),
            text=text_vals,
            textposition="outside",
            textfont=dict(
                size=11, color=style.colour, family=tokens.font_mono,
            ),
            hovertemplate=(
                f"<b>{style.label}</b><br>"
                f"%{{x}}<br>Value: %{{text}}<extra></extra>"
            ),
        ))

    # Let Plotly auto-size the y-axis to fit bar labels (textposition="outside")
    # autorange + rangemode ensures it starts from 0 and expands to fit text
    layout["yaxis"]["autorange"] = True
    layout["yaxis"]["rangemode"] = "tozero"
    layout.setdefault("margin", {})["t"] = 60

    fig.update_layout(**layout)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# PIE / DONUT CHART
# ═════════════════════════════════════════════════════════════════════════════

def pie_chart(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    formatter: Callable[[float], str] = fmt_currency,
    title: str = "",
    height: int = 400,
    hole: float = 0.45,
    tokens: Optional[ThemeTokens] = None,
) -> go.Figure:
    """
    Pie or donut chart for composition analysis.

    Great for showing:
      - Revenue mix by product ("Casino is 40% of revenue")
      - Brand share of stakes
      - Cost breakdown

    Parameters
    ----------
    df : DataFrame
        Data to plot.
    label_col : str
        Column with category labels (e.g. "product", "brand").
    value_col : str
        Column with numeric values to plot.
    formatter : Callable
        How to format values in labels/tooltips.
    title : str
        Chart title.
    height : int
        Chart height in pixels. Default 400.
    hole : float
        Size of the center hole (0 = full pie, 0.45 = donut). Default 0.45.
    tokens : ThemeTokens, optional
        Theme palette. Defaults to active theme.

    Returns
    -------
    go.Figure
    """
    if tokens is None:
        tokens = get_active_theme()

    colours = tokens.chart_series
    layout = base_layout(tokens, height=height, show_legend=True)
    layout["title"] = dict(
        text=title,
        font=dict(size=13, color=tokens.text_muted),
        x=0.01,
    )

    # Pre-format values for the hover text
    formatted_vals = [formatter(v) for v in df[value_col]]

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=df[label_col],
        values=df[value_col],
        hole=hole,
        marker=dict(
            colors=[colours[i % len(colours)] for i in range(len(df))],
            line=dict(color=tokens.bg_surface, width=2),
        ),
        textinfo="percent+label",
        textfont=dict(size=11, family=tokens.font_primary),
        customdata=formatted_vals,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: %{customdata}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    ))

    fig.update_layout(**layout)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# WATERFALL CHART (bridge / driver analysis)
# ═════════════════════════════════════════════════════════════════════════════

def waterfall_chart(
    categories: List[str],
    values: List[float],
    formatter: Callable[[float], str] = fmt_currency,
    title: str = "",
    height: int = 420,
    base_label: str = "LY",
    result_label: str = "TY",
    tokens: Optional[ThemeTokens] = None,
) -> go.Figure:
    """
    Waterfall (bridge) chart for variance/driver analysis.

    Shows how a starting value transforms into an ending value through
    a series of positive and negative changes. Standard in finance for
    "what drove the YoY change in revenue?"

    Parameters
    ----------
    categories : list[str]
        Labels for each bar: [start, driver1, driver2, ..., end].
        Example: ["LY Revenue", "Volume", "Price", "Mix", "TY Revenue"]
    values : list[float]
        Values for each bar. The first and last should be absolute totals,
        middle values are the incremental changes (positive or negative).
        Example: [100000, 15000, -3000, 2000, 114000]
    formatter : Callable
        How to format bar labels.
    title : str
        Chart title.
    height : int
        Chart height in pixels. Default 420.
    base_label : str
        Label for the starting total bar. Default "LY".
    result_label : str
        Label for the ending total bar. Default "TY".
    tokens : ThemeTokens, optional
        Theme palette. Defaults to active theme.

    Returns
    -------
    go.Figure

    Example
    -------
    fig = waterfall_chart(
        categories=["LY Revenue", "Volume Effect", "Price Effect",
                     "Mix Effect", "TY Revenue"],
        values=[100000, 15000, -3000, 2000, 114000],
        formatter=fmt_currency,
        title="Revenue Bridge — LY to TY",
    )
    """
    if tokens is None:
        tokens = get_active_theme()

    layout = base_layout(tokens, height=height)
    layout["title"] = dict(
        text=title,
        font=dict(size=13, color=tokens.text_muted),
        x=0.01,
    )

    # Determine measure types: first and last are "absolute", rest are "relative"
    n = len(categories)
    measures = []
    for i in range(n):
        if i == 0 or i == n - 1:
            measures.append("absolute")
        else:
            measures.append("relative")

    # Colour each bar: totals = accent, positive = green, negative = red
    bar_colours = []
    for i, (m, v) in enumerate(zip(measures, values)):
        if m == "absolute":
            bar_colours.append(tokens.accent)
        elif v >= 0:
            bar_colours.append(tokens.positive)
        else:
            bar_colours.append(tokens.negative)

    text_vals = [formatter(v) for v in values]

    fig = go.Figure()
    fig.add_trace(go.Waterfall(
        x=categories,
        y=values,
        measure=measures,
        text=text_vals,
        textposition="outside",
        textfont=dict(size=11, family=tokens.font_mono, color=tokens.text_primary),
        connector=dict(line=dict(color=tokens.border, width=1)),
        increasing=dict(marker=dict(color=tokens.positive)),
        decreasing=dict(marker=dict(color=tokens.negative)),
        totals=dict(marker=dict(color=tokens.accent)),
        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
    ))

    fig.update_layout(**layout)
    return fig
