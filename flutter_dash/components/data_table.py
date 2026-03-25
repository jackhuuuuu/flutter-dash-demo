# flutter_dash/components/data_table.py
"""
Hierarchical financial data table.

Renders a styled HTML table with:
  - A Grand Total row
  - Group-level summary rows (e.g. by brand)
  - Detail-level rows (e.g. by product within brand)
  - For each metric: Value | YoY Delta | YoY % | Budget Var | Budget %

Fully dynamic:
  - Pass any list of MetricDef objects (not limited to 5 hardcoded metrics)
  - Pass any group_by columns (not limited to brand → product)
  - Formatters come from each MetricDef, so different metrics can use
    different formatting (currency, %, number)

Standard finance variance sub-columns:
  Value   — This Year's actual value
  YoY Δ   — Absolute difference vs Last Year
  YoY %   — Relative difference vs Last Year
  Bud Var — Absolute difference vs Budget
  Bud %   — Relative difference vs Budget
"""

import streamlit as st
import pandas as pd
from typing import List, Optional

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import ThemeTokens, hex_to_rgba
from flutter_dash.helpers import MetricDef
from flutter_dash.formatters import fmt_table_thousands


# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL: Weighted average helper
# ═════════════════════════════════════════════════════════════════════════════

def _weighted_avg(df: pd.DataFrame, value_col: str, weight_col: str) -> float:
    """Compute a weighted average. Returns 0.0 if weights sum to zero."""
    valid = df[[value_col, weight_col]].dropna()
    w_sum = valid[weight_col].sum()
    if w_sum <= 0:
        return 0.0
    return (valid[value_col] * valid[weight_col]).sum() / w_sum


# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL: Aggregate one metric from a DataFrame slice
# ═════════════════════════════════════════════════════════════════════════════

def _aggregate_metric(df: pd.DataFrame, m: MetricDef) -> dict:
    """
    Aggregate a single MetricDef from a DataFrame.

    For simple sum metrics (is_pct=False, no weight_col):
      → just sum the columns

    For weighted average metrics (is_pct=True, weight_col set):
      → compute weighted average using the weight column
    """
    if m.weight_col and m.is_pct:
        # Weighted average (e.g. margin weighted by stakes)
        ty = _weighted_avg(df, m.ty_col, m.weight_col)
        # For LY and Budget, the weight column name follows a pattern:
        # If ty_col="margin" and weight_col="total_stakes",
        # then ly weight = "total_stakes_ly", bud weight = "total_stakes_budget"
        # We derive these from the metric's own ly/bud column naming.
        #
        # Actually, we need the weight columns for LY and Budget too.
        # Convention: if weight_col is "total_stakes", then:
        #   LY weight  = weight_col + "_ly"
        #   Bud weight = weight_col + "_budget"
        w_ly = m.weight_col + "_ly"
        w_bud = m.weight_col + "_budget"
        ly = _weighted_avg(df, m.ly_col, w_ly) if w_ly in df.columns else 0.0
        bud = _weighted_avg(df, m.bud_col, w_bud) if w_bud in df.columns else 0.0
    else:
        # Simple sum
        ty = df[m.ty_col].sum() if m.ty_col in df.columns else 0.0
        ly = df[m.ly_col].sum() if m.ly_col in df.columns else 0.0
        bud = df[m.bud_col].sum() if m.bud_col in df.columns else 0.0

    return {"ty": ty, "ly": ly, "bud": bud}


# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL: Format variance sub-columns
# ═════════════════════════════════════════════════════════════════════════════

def _format_variances(ty, ly, bud, m: MetricDef, table_fmt=None):
    """
    Calculate and format the 5 sub-columns for one metric:
      val_str, yoy_d_str, yoy_p_str, bud_v_str, bud_p_str, yoy_d_raw, bud_v_raw

    Returns raw deltas (yoy_d_raw, bud_v_raw) for colour-coding.

    Parameters
    ----------
    table_fmt : Callable, optional
        Override formatter for non-pct metrics (e.g. fmt_table_thousands).
    """
    yoy_d = (ty - ly) if ly else 0.0
    yoy_p = yoy_d / abs(ly) if ly else 0.0
    bud_v = (ty - bud) if bud else 0.0
    bud_p = bud_v / abs(bud) if bud else 0.0

    if m.is_pct:
        # Percentage metrics: deltas in percentage points (pp)
        return (
            m.formatter(ty),
            f"{yoy_d * 100:+.2f}pp",
            f"{yoy_p * 100:.1f}%",
            f"{bud_v * 100:+.2f}pp",
            f"{bud_p * 100:.1f}%",
            yoy_d,
            bud_v,
        )
    else:
        fmt = table_fmt if table_fmt else m.formatter
        return (
            fmt(ty),
            fmt(yoy_d),
            f"{yoy_p * 100:.1f}%",
            fmt(bud_v),
            f"{bud_p * 100:.1f}%",
            yoy_d,
            bud_v,
        )


# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL: HTML cell builder functions
# ═════════════════════════════════════════════════════════════════════════════

def _pos_neg_colour(val: float, tokens: ThemeTokens) -> str:
    """Return green/red/grey colour for a variance value."""
    if val > 0:
        return tokens.positive
    if val < 0:
        return tokens.negative
    return tokens.text_muted


def _th_metric(label: str, tokens: ThemeTokens, span: int = 5) -> str:
    """Metric group header cell (spans 5 sub-columns)."""
    return (
        f"<th colspan='{span}' style='"
        f"padding:10px 8px 6px;text-align:center;"
        f"border-bottom:1px solid {tokens.accent}44;"
        f"border-left:2px solid {tokens.border};"
        f"color:{tokens.accent};font-size:12px;font-weight:700;"
        f"text-transform:uppercase;letter-spacing:.09em;"
        f"background:{tokens.bg_elevated};white-space:nowrap;"
        f"'>{label}</th>"
    )


def _th_dim(label: str, tokens: ThemeTokens) -> str:
    """Dimension header cell (rowspan=2 to span both header rows)."""
    return (
        f"<th rowspan='2' style='"
        f"padding:10px 12px;vertical-align:middle;"
        f"border-bottom:2px solid {tokens.border};"
        f"color:{tokens.text_muted};font-size:11px;"
        f"text-transform:uppercase;letter-spacing:.07em;"
        f"background:{tokens.bg_elevated};white-space:nowrap;"
        f"'>{label}</th>"
    )


def _th_sub(label: str, tokens: ThemeTokens, first_in_group: bool = False) -> str:
    """Sub-column header (Value, YoY Δ, YoY %, Bud Var, Bud %)."""
    left_border = f"border-left:2px solid {tokens.border};" if first_in_group else ""
    return (
        f"<th style='"
        f"padding:6px 8px 8px;text-align:right;"
        f"border-bottom:2px solid {tokens.border};"
        f"{left_border}"
        f"color:{tokens.text_muted};font-size:10px;"
        f"text-transform:uppercase;letter-spacing:.06em;"
        f"background:{tokens.bg_elevated};white-space:nowrap;"
        f"'>{label}</th>"
    )


def _td_dim(label: str, level: int, tokens: ThemeTokens) -> str:
    """
    Dimension cell in the data body.

    level 0 = Grand Total (accent colour, bold)
    level 1 = Group      (primary text, bold)
    level 2 = Detail     (muted text, indented with ▸ prefix)
    """
    styles = [
        # Level 0 — Grand Total
        dict(
            color=tokens.accent, fw="700", bg=hex_to_rgba(tokens.accent, 0.07),
            pl="12px", prefix="", fs="13px",
            bt=f"border-top:2px solid {tokens.accent}44;",
        ),
        # Level 1 — Group summary
        dict(
            color=tokens.text_primary, fw="700", bg=tokens.bg_elevated,
            pl="14px", prefix="", fs="13px",
            bt=f"border-top:1px solid {tokens.border};",
        ),
        # Level 2 — Detail row
        dict(
            color=tokens.text_muted, fw="400", bg=tokens.bg_surface,
            pl="28px", prefix="▸ ", fs="12px",
            bt="",
        ),
    ]
    s = styles[min(level, 2)]  # Clamp to max level 2
    return (
        f"<td style='padding:9px {s['pl']};"
        f"border-bottom:1px solid {tokens.border};{s['bt']}"
        f"background:{s['bg']};font-weight:{s['fw']};color:{s['color']};"
        f"font-size:{s['fs']};white-space:nowrap;'>"
        f"{s['prefix']}{label}</td>"
    )


def _td_val(
    val_str: str, level: int, tokens: ThemeTokens,
    first_in_group: bool = False,
) -> str:
    """Value cell (right-aligned, monospace font)."""
    accent_bg = hex_to_rgba(tokens.accent, 0.07)
    bgs = [accent_bg, tokens.bg_elevated, tokens.bg_surface]
    fws = ["700", "700", "400"]
    fss = ["13px", "12px", "12px"]
    border = f"border-left:2px solid {tokens.border};" if first_in_group else ""
    bt = (
        f"border-top:2px solid {tokens.accent}44;" if level == 0
        else f"border-top:1px solid {tokens.border};" if level == 1
        else ""
    )
    lv = min(level, 2)
    return (
        f"<td style='padding:9px 8px;text-align:right;"
        f"border-bottom:1px solid {tokens.border};{border}{bt}"
        f"background:{bgs[lv]};color:{tokens.text_primary};"
        f"font-weight:{fws[lv]};"
        f"font-family:{tokens.font_mono};font-size:{fss[lv]};white-space:nowrap;'>"
        f"{val_str}</td>"
    )


def _td_delta(
    val_str: str, raw_delta: float, level: int, tokens: ThemeTokens,
) -> str:
    """Delta cell — colour-coded green/red based on variance direction."""
    col = _pos_neg_colour(raw_delta, tokens)
    accent_bg = hex_to_rgba(tokens.accent, 0.07)
    bgs = [accent_bg, tokens.bg_elevated, tokens.bg_surface]
    fws = ["700", "700", "400"]
    fss = ["13px", "12px", "12px"]
    bt = (
        f"border-top:2px solid {tokens.accent}44;" if level == 0
        else f"border-top:1px solid {tokens.border};" if level == 1
        else ""
    )
    lv = min(level, 2)
    return (
        f"<td style='padding:9px 8px;text-align:right;"
        f"border-bottom:1px solid {tokens.border};{bt}"
        f"background:{bgs[lv]};color:{col};"
        f"font-weight:{fws[lv]};"
        f"font-family:{tokens.font_mono};font-size:{fss[lv]};white-space:nowrap;'>"
        f"{val_str}</td>"
    )


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC: data_table
# ═════════════════════════════════════════════════════════════════════════════

def data_table(
    df: pd.DataFrame,
    metrics: List[MetricDef],
    group_by: List[str],
    title: str = "",
    dim_header: Optional[str] = None,
    tokens: Optional[ThemeTokens] = None,
    currency_unit: Optional[str] = None,
) -> None:
    """
    Render a hierarchical financial table.

    Structure:
      Grand Total  (all data)
        Group A    (e.g. Brand A — aggregated)
          └ Detail 1  (e.g. Sportsbook)
          └ Detail 2  (e.g. Casino)
        Group B    (e.g. Brand B — aggregated)
          └ Detail 1
          ...

    Parameters
    ----------
    df : DataFrame
        Filtered data to display.
    metrics : list[MetricDef]
        Which metrics to show. Each MetricDef defines the column names,
        formatter, and whether it's a percentage metric.
        Can be 3 metrics, 5 metrics, or any number.
    group_by : list[str]
        Hierarchy of grouping columns, e.g. ["brand", "product"].
        First column = group level, second = detail level.
        Currently supports 1 or 2 levels of grouping.
    title : str, optional
        Text above the table.
    dim_header : str, optional
        Header label for the dimension column. If None, auto-generated
        from group_by columns (e.g. "Brand / Product").
    tokens : ThemeTokens, optional
        Theme palette. Defaults to active theme.

    Examples
    --------
    from flutter_dash.formatters import fmt_currency, fmt_pct
    from flutter_dash.helpers import MetricDef

    metrics = [
        MetricDef("Net Revenue", "total_net_revenue", "total_net_revenue_ly",
                  "total_net_revenue_budget", fmt_currency),
        MetricDef("Margin %", "margin", "margin_ly", "margin_budget",
                  fmt_pct, is_pct=True, weight_col="total_stakes"),
    ]

    data_table(df, metrics=metrics, group_by=["brand", "product"])
    """
    if tokens is None:
        tokens = get_active_theme()

    if df.empty:
        st.info("No data available for the selected filters.")
        return

    # ── Auto-generate dimension header ────────────────────────────────────────
    if dim_header is None:
        dim_header = " / ".join(col.replace("_", " ").title() for col in group_by)

    # ── Determine table formatter based on currency_unit ──────────────────────
    table_fmt = None
    unit_suffix = ""
    if currency_unit == "thousands":
        table_fmt = fmt_table_thousands
        unit_suffix = " (£'000s)"

    # ── Build metric cells for one aggregated row ─────────────────────────────
    def build_metric_cells(sub_df: pd.DataFrame, level: int) -> str:
        cells = ""
        for i, m in enumerate(metrics):
            first = (i == 0)
            agg = _aggregate_metric(sub_df, m)
            fmt_override = table_fmt if (table_fmt and not m.is_pct) else None
            v, yd, yp, bv, bp, yoy_d, bud_v = _format_variances(
                agg["ty"], agg["ly"], agg["bud"], m, table_fmt=fmt_override
            )
            cells += _td_val(v, level, tokens, first_in_group=first)
            cells += _td_delta(yd, yoy_d, level, tokens)
            cells += _td_delta(yp, yoy_d, level, tokens)
            cells += _td_delta(bv, bud_v, level, tokens)
            cells += _td_delta(bp, bud_v, level, tokens)
        return cells

    # ── Headers ───────────────────────────────────────────────────────────────
    # Row 1: dimension header + metric group headers
    header1 = "<tr>" + _th_dim(dim_header, tokens)
    for m in metrics:
        label = m.label + unit_suffix if (unit_suffix and not m.is_pct) else m.label
        header1 += _th_metric(label, tokens)
    header1 += "</tr>"

    # Row 2: sub-column headers (Value, YoY Δ, YoY %, Bud Var, Bud %)
    sub_labels = ["Value", "YoY Δ", "YoY %", "Bud Var", "Bud %"]
    sub_cells = ""
    for i in range(len(metrics)):
        for j, sc in enumerate(sub_labels):
            sub_cells += _th_sub(sc, tokens, first_in_group=(j == 0))
    header2 = f"<tr>{sub_cells}</tr>"

    # ── Body ──────────────────────────────────────────────────────────────────
    body_html = ""

    # Level 0: Grand Total
    body_html += (
        "<tr>"
        + _td_dim("Grand Total", 0, tokens)
        + build_metric_cells(df, 0)
        + "</tr>"
    )

    # Level 1 + 2: Group → Detail
    if len(group_by) >= 1:
        group_col = group_by[0]
        for group_val in sorted(df[group_col].unique()):
            df_group = df[df[group_col] == group_val]
            body_html += (
                "<tr>"
                + _td_dim(str(group_val), 1, tokens)
                + build_metric_cells(df_group, 1)
                + "</tr>"
            )

            # Detail level (if we have a second grouping column)
            if len(group_by) >= 2:
                detail_col = group_by[1]
                for detail_val in sorted(df_group[detail_col].unique()):
                    df_detail = df_group[df_group[detail_col] == detail_val]
                    body_html += (
                        "<tr>"
                        + _td_dim(str(detail_val), 2, tokens)
                        + build_metric_cells(df_detail, 2)
                        + "</tr>"
                    )

    # ── Render ────────────────────────────────────────────────────────────────
    table_html = f"""
    <div style="overflow-x:auto;border-radius:12px;
                border:1px solid {tokens.border};
                background:{tokens.bg_surface};
                margin-top:8px;">
      <table style="border-collapse:collapse;width:100%;
                    font-family:{tokens.font_primary};
                    font-size:13px;color:{tokens.text_primary};">
        <thead>{header1}{header2}</thead>
        <tbody>{body_html}</tbody>
      </table>
    </div>
    """

    if title:
        st.markdown(
            f'<p style="color:{tokens.text_muted};font-size:12px;'
            f'text-transform:uppercase;letter-spacing:.08em;'
            f'margin-bottom:8px;">{title}</p>',
            unsafe_allow_html=True,
        )
    st.markdown(table_html, unsafe_allow_html=True)
