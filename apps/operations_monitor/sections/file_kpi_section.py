# sections/file_kpi_section.py
"""
KPI cards for the File Delivery tab.

Displays headline metrics:
  - Total Files: unique file/date combinations in the period
  - ERP Delivered: files that have reached ERP-quality status
  - EPM Only: files still waiting for ERP sign-off
  - Avg ERP Delivery Days: average days from reporting_date to ERP delivery
"""

import streamlit as st
import pandas as pd

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import hex_to_rgba
from flutter_dash.components import section_title

from config import (
    COL_ERP_FINAL_DELIVERED_AT, COL_ERP_FINAL_RESENT_AT,
    COL_ERP_DELIVERY_DAYS, COL_DELIVERY_LIFECYCLE,
    COL_REPORTING_DATE,
    STATUS_PASS, STATUS_FAIL,
    DELIVERY_ERP_DELIVERED, DELIVERY_EPM_ONLY, DELIVERY_MANUAL_OVERRIDE,
)


def _render_ops_kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    colour: str = "",
    icon: str = "",
    card_index: int = 0,
) -> None:
    """Render a simple operational KPI card."""
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
    st.html(card_html)


def render_file_kpi_section(df: pd.DataFrame) -> None:
    """
    Render KPI cards for the file delivery tab.

    Parameters
    ----------
    df : DataFrame
        Filtered file delivery data.
    """
    section_title("Delivery Health", "File delivery status summary")

    if df.empty:
        st.warning("No data available for the selected filters.")
        return

    tokens = get_active_theme()

    total_files = len(df)

    # ERP delivery based on erp_final_delivered_at (not null = delivered)
    erp_delivered = df[COL_ERP_FINAL_DELIVERED_AT].notna().sum()
    epm_only = (df[COL_DELIVERY_LIFECYCLE] == DELIVERY_EPM_ONLY).sum()
    manual_count = (df[COL_DELIVERY_LIFECYCLE] == DELIVERY_MANUAL_OVERRIDE).sum()

    erp_rate = (erp_delivered / total_files * 100) if total_files > 0 else 0

    # Late files: delivery days > 1 (based on erp_final_delivered_at timing)
    erp_days = df[COL_ERP_DELIVERY_DAYS].dropna()
    avg_erp_days = erp_days.mean() if len(erp_days) > 0 else 0
    late_files = int((erp_days > 1).sum())

    # Resent files: erp_final_resent_at is not null
    resent_count = df[COL_ERP_FINAL_RESENT_AT].notna().sum()

    # Colours
    erp_colour = tokens.positive if erp_rate >= 95 else (
        tokens.warning if erp_rate >= 80 else tokens.negative
    )
    epm_colour = tokens.negative if epm_only > 0 else tokens.positive

    cols = st.columns(5)

    with cols[0]:
        _render_ops_kpi_card(
            title="ERP Delivery Rate",
            value=f"{erp_rate:.1f}%",
            subtitle=f"{erp_delivered:,} of {total_files:,} delivered",
            colour=erp_colour,
            icon="✅",
            card_index=10,
        )

    with cols[1]:
        _render_ops_kpi_card(
            title="EPM Only",
            value=f"{epm_only}",
            subtitle="Waiting for ERP sign-off" if epm_only > 0 else "All files at ERP",
            colour=epm_colour,
            icon="⏳" if epm_only > 0 else "✅",
            card_index=11,
        )

    with cols[2]:
        _render_ops_kpi_card(
            title="Manual Overrides",
            value=f"{manual_count}",
            subtitle="Manually approved files",
            colour=tokens.warning if manual_count > 0 else tokens.text_muted,
            icon="🔒" if manual_count > 0 else "—",
            card_index=12,
        )

    with cols[3]:
        late_colour = tokens.negative if late_files > 0 else tokens.positive
        _render_ops_kpi_card(
            title="Late Deliveries",
            value=f"{late_files}",
            subtitle=f"Files > 1 day (avg {avg_erp_days:.1f}d)",
            colour=late_colour,
            icon="⚠️" if late_files > 0 else "✅",
            card_index=13,
        )

    with cols[4]:
        _render_ops_kpi_card(
            title="ERP Resends",
            value=f"{resent_count}",
            subtitle="Files re-sent after initial ERP",
            colour=tokens.warning if resent_count > 0 else tokens.text_muted,
            icon="🔄" if resent_count > 0 else "—",
            card_index=14,
        )
