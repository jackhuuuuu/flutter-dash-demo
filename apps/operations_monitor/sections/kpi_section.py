# sections/kpi_section.py
"""
KPI cards section — headline metrics for the Operations Monitor.

Displays key operational health indicators:
  - Total Checks: how many check/date combinations exist
  - Pass Rate: percentage of checks currently passing
  - Active Failures: count of checks with FAIL status right now
  - Unresolved Issues: checks that failed and haven't been fixed yet
  - Avg Resolution Time: how long it typically takes to fix a failure
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import hex_to_rgba
from flutter_dash.components import section_title

from config import (
    COL_OVERALL_STATUS, COL_REV_LIFECYCLE, COL_EPM_LIFECYCLE,
    COL_REV_RESOLUTION_MINS, COL_EPM_RESOLUTION_MINS,
    STATUS_PASS, STATUS_FAIL,
    LIFECYCLE_UNRESOLVED, LIFECYCLE_RESOLVED,
)


def _render_ops_kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    colour: str = "",
    icon: str = "",
    card_index: int = 0,
) -> None:
    """
    Render a simple operational KPI card (no variance comparisons).

    Unlike the finance KPI cards which compare TY vs LY, these cards
    show a single value with contextual colouring (green = healthy,
    red = needs attention).

    Parameters
    ----------
    title : str
        Metric name (e.g. "Pass Rate").
    value : str
        Pre-formatted display value (e.g. "98.5%").
    subtitle : str
        Extra context line below the value (e.g. "4 of 440 failing").
    colour : str
        Accent colour for the value text (from theme tokens).
    icon : str
        Emoji icon shown next to the title.
    card_index : int
        Unique index for HTML element IDs.
    """
    tokens = get_active_theme()

    if not colour:
        colour = tokens.accent

    accent_bg = hex_to_rgba(colour, 0.10)

    card_html = f"""
    <!DOCTYPE html><html><head>
    <style>
      * {{ box-sizing:border-box; }}
      html, body {{
        margin:0; padding:0;
        background:transparent;
        font-family:{tokens.font_primary};
        color:{tokens.text_primary};
        overflow:hidden;
      }}
      .card {{
        background:{tokens.bg_surface};
        border:1px solid {tokens.border};
        border-radius:14px;
        padding:18px 16px;
        height:140px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
      }}
      .card-title {{
        font-size:11px;
        font-weight:600;
        text-transform:uppercase;
        letter-spacing:0.08em;
        color:{tokens.text_muted};
        margin:0 0 8px 0;
      }}
      .card-value {{
        font-size:28px;
        font-weight:700;
        color:{colour};
        font-family:{tokens.font_mono};
        margin:0;
        line-height:1.2;
      }}
      .card-subtitle {{
        font-size:11px;
        color:{tokens.text_muted};
        margin:4px 0 0 0;
      }}
      .icon-pill {{
        display:inline-block;
        background:{accent_bg};
        border-radius:6px;
        padding:2px 8px;
        font-size:10px;
        color:{colour};
        font-weight:600;
        margin-bottom:4px;
      }}
    </style>
    </head><body>
    <div class="card">
      <div>
        <span class="icon-pill">{icon}</span>
        <p class="card-title">{title}</p>
      </div>
      <div>
        <p class="card-value">{value}</p>
        <p class="card-subtitle">{subtitle}</p>
      </div>
    </div>
    </body></html>
    """
    st.html(card_html, height=155)


def render_kpi_section(df: pd.DataFrame) -> None:
    """
    Render the KPI cards row at the top of the dashboard.

    Parameters
    ----------
    df : DataFrame
        Filtered dataset for the current sidebar selections.
    """
    section_title("Operational Health", "Current DQ check status summary")

    if df.empty:
        st.warning("No data available for the selected filters.")
        return

    tokens = get_active_theme()

    # ── Calculate KPI values ──────────────────────────────────────────────
    total_checks = len(df)
    pass_count = (df[COL_OVERALL_STATUS] == STATUS_PASS).sum()
    fail_count = (df[COL_OVERALL_STATUS] == STATUS_FAIL).sum()
    pass_rate = (pass_count / total_checks * 100) if total_checks > 0 else 0

    # Resolved = checks that failed but have since been fixed
    resolved = df[
        (df[COL_REV_LIFECYCLE] == LIFECYCLE_RESOLVED)
        | (df[COL_EPM_LIFECYCLE] == LIFECYCLE_RESOLVED)
    ].shape[0]

    # Average resolution time across both revenue and EPM (in hours)
    rev_mins = df[COL_REV_RESOLUTION_MINS].dropna()
    epm_mins = df[COL_EPM_RESOLUTION_MINS].dropna()
    all_mins = pd.concat([rev_mins, epm_mins])
    avg_resolution_hrs = (all_mins.mean() / 60) if len(all_mins) > 0 else 0

    # ── Choose colours based on values ────────────────────────────────────
    pass_colour = tokens.positive if pass_rate >= 95 else (
        tokens.warning if pass_rate >= 80 else tokens.negative
    )
    fail_colour = tokens.positive if fail_count == 0 else tokens.negative
    resolved_colour = tokens.positive if resolved > 0 else tokens.text_muted

    # ── Render 5 KPI cards in columns ─────────────────────────────────────
    cols = st.columns(5)

    with cols[0]:
        _render_ops_kpi_card(
            title="Total Checks",
            value=f"{total_checks:,}",
            subtitle=f"Across {df['reporting_date'].nunique()} days",
            colour=tokens.accent,
            icon="📋",
            card_index=0,
        )

    with cols[1]:
        _render_ops_kpi_card(
            title="Pass Rate",
            value=f"{pass_rate:.1f}%",
            subtitle=f"{pass_count:,} of {total_checks:,} passing",
            colour=pass_colour,
            icon="✅",
            card_index=1,
        )

    with cols[2]:
        _render_ops_kpi_card(
            title="Active Failures",
            value=f"{fail_count}",
            subtitle="Currently failing" if fail_count > 0 else "All checks passing",
            colour=fail_colour,
            icon="🚨" if fail_count > 0 else "✅",
            card_index=2,
        )

    with cols[3]:
        _render_ops_kpi_card(
            title="Resolved Issues",
            value=f"{resolved}",
            subtitle="Previously failed, now fixed" if resolved > 0 else "No failures recorded",
            colour=resolved_colour,
            icon="🔧" if resolved > 0 else "—",
            card_index=3,
        )

    with cols[4]:
        _render_ops_kpi_card(
            title="Avg Resolution Time",
            value=f"{avg_resolution_hrs:.1f}h",
            subtitle=f"{len(all_mins)} resolved failures" if len(all_mins) > 0 else "No data",
            colour=tokens.accent,
            icon="⏱️",
            card_index=4,
        )
