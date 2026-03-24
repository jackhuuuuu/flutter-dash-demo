# flutter_dash/theme/plotly.py
"""
Plotly layout builder — creates chart layouts from theme tokens.

Every Plotly chart in the dashboard uses this as its base layout, so charts
automatically pick up the right colours, fonts, and grid styles from the
active theme.
"""

from flutter_dash.theme.tokens import ThemeTokens


def base_layout(tokens: ThemeTokens, height: int = 350, show_legend: bool = True) -> dict:
    """
    Create a Plotly layout dict styled to match the active theme.

    Parameters
    ----------
    tokens : ThemeTokens
        The active palette (colours, fonts).
    height : int
        Chart height in pixels. Default 350.
    show_legend : bool
        Whether to show the chart legend. Default True.

    Returns
    -------
    dict
        A layout dict you pass to fig.update_layout(**layout).
    """
    return dict(
        height=height,
        paper_bgcolor=tokens.bg_surface,
        plot_bgcolor=tokens.bg_surface,
        font=dict(
            family=tokens.font_primary,
            color=tokens.text_primary,
            size=12,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
            visible=show_legend,
        ),
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(
            gridcolor=tokens.chart_grid,
            linecolor=tokens.border,
            tickfont=dict(size=10, color=tokens.text_muted),
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor=tokens.chart_grid,
            linecolor=tokens.border,
            tickfont=dict(size=10, color=tokens.text_muted),
            showgrid=True,
            gridwidth=1,
        ),
        hoverlabel=dict(
            bgcolor=tokens.bg_elevated,
            bordercolor=tokens.border,
            font=dict(
                family=tokens.font_primary,
                size=12,
                color=tokens.text_primary,
            ),
        ),
    )
