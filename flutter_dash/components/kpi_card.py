# flutter_dash/components/kpi_card.py
"""
KPI Card — displays a key metric with variance comparisons.

Features:
  - Large headline value with period pill
  - Any number of comparison rows (vs LY, vs Budget, vs Forecast, etc.)
  - Optional "drivers" panel showing what caused the variance
  - Automatically colour-coded: green = favourable, red = adverse

The card uses an HTML iframe (stc.html) for rich styling. The flip
animation between front/back is handled by minimal JavaScript inside
the iframe — you don't need to understand it, it just works.
"""

import streamlit as st
import streamlit.components.v1 as stc
from typing import Callable, Dict, List, Optional

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import ThemeTokens
from flutter_dash.formatters import fmt_currency, fmt_pct
from flutter_dash.helpers import delta_colour, delta_arrow, Comparison


def kpi_card(
    title: str,
    value: float,
    comparisons: List[Comparison],
    formatter: Callable[[float], str] = fmt_currency,
    drivers: Optional[Dict[str, float]] = None,
    driver_formatter: Optional[Callable[[float], str]] = None,
    flippable: bool = False,
    card_index: int = 0,
    period_label: str = "MTD",
    is_pct: bool = False,
    tokens: Optional[ThemeTokens] = None,
    height: int = 255,
) -> None:
    """
    Render a styled KPI card.

    Parameters
    ----------
    title : str
        Metric name (e.g. "Net Revenue", "Margin %").
    value : float
        The headline value to display.
    comparisons : list[Comparison]
        Variance rows to show. Each has a label, ref_value, delta, and delta_pct.
        Example: [Comparison("vs LY", 100000, 12000, 0.12),
                  Comparison("vs Bud", 110000, 2000, 0.018)]
    formatter : Callable
        How to format the headline value and reference values.
        Use fmt_currency for money, fmt_pct for percentages.
    drivers : dict, optional
        Driver breakdown (e.g. {"Volume Effect": 5000, "Price Effect": 3000}).
        Only shown if flippable=True.
    driver_formatter : Callable, optional
        How to format driver values. Defaults to fmt_currency.
    flippable : bool
        Whether the card can flip to show drivers.
    card_index : int
        Unique index for this card (used internally for HTML element IDs).
    period_label : str
        Period pill text (e.g. "MTD", "WTD", "Yesterday").
    is_pct : bool
        True for percentage metrics — deltas shown in pp (percentage points).
    tokens : ThemeTokens, optional
        Theme to use. Defaults to active theme.
    height : int
        Card height in pixels. Default 255.
    """
    if tokens is None:
        tokens = get_active_theme()
    if driver_formatter is None:
        driver_formatter = fmt_currency

    # ── Format the headline value ─────────────────────────────────────────────
    val_str = formatter(value)

    # ── Build comparison rows HTML ────────────────────────────────────────────
    compare_html = ""
    for comp in comparisons:
        # Colour and arrow based on the delta direction
        col = delta_colour(comp.delta, tokens)
        arr = delta_arrow(comp.delta)

        # Format the reference value and deltas
        ref_str = formatter(comp.ref_value)
        if is_pct:
            delta_str = f"{comp.delta * 100:+.2f}pp"
        else:
            delta_str = formatter(comp.delta)
        pct_str = f"{comp.delta_pct * 100:.1f}%"

        compare_html += f"""
        <div class="compare-block">
          <div class="compare-row">
            <span class="compare-label">{comp.label}</span>
            <span class="ref-value">{ref_str}</span>
            <span class="divider"></span>
            <span class="badge" style="background:{col}22;color:{col};">
              {arr} {delta_str}
            </span>
            <span class="badge" style="background:{col}22;color:{col};">
              {arr} {pct_str}
            </span>
          </div>
        </div>
        """

    # ── Build drivers HTML (back of card) ─────────────────────────────────────
    drivers_html = ""
    if flippable and drivers:
        total = sum(abs(v) for v in drivers.values()) or 1
        rows = ""
        for d_name, d_val in drivers.items():
            d_col = delta_colour(d_val, tokens)
            d_arr = delta_arrow(d_val)
            d_pct = d_val / total * 100
            rows += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:5px 0;border-bottom:1px solid {tokens.border};">
              <span style="color:{tokens.text_muted};font-size:11px;">{d_name}</span>
              <span style="color:{d_col};font-size:12px;font-weight:600;text-align:right;">
                {d_arr} {driver_formatter(abs(d_val))}
                <span style="font-size:10px;opacity:.75;"> ({d_pct:.1f}%)</span>
              </span>
            </div>"""
        drivers_html = f"""
        <div style="margin-top:4px;">
          <div style="color:{tokens.text_muted};font-size:10px;
                      text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">
            Drivers — YoY
          </div>
          {rows}
        </div>"""

    # ── Flip buttons ──────────────────────────────────────────────────────────
    front_id = f"front_{card_index}"
    back_id = f"back_{card_index}"

    flip_btn = ""
    if flippable and drivers:
        flip_btn = f"""
        <div style="margin-top:12px;border-top:1px solid {tokens.border};padding-top:8px;">
          <button onclick="
            document.getElementById('{front_id}').style.display='none';
            document.getElementById('{back_id}').style.display='block';
          " style="background:rgba(0,212,255,0.1);border:1px solid {tokens.accent};
                   cursor:pointer;color:{tokens.accent};font-size:11px;
                   border-radius:6px;padding:4px 12px;width:100%;
                   text-transform:uppercase;letter-spacing:.07em;font-weight:600;">
            &#x27F3; View Drivers
          </button>
        </div>"""

    back_btn = f"""
    <div style="margin-top:10px;border-top:1px solid {tokens.border};padding-top:8px;">
      <button onclick="
        document.getElementById('{back_id}').style.display='none';
        document.getElementById('{front_id}').style.display='block';
      " style="background:rgba(0,212,255,0.1);border:1px solid {tokens.accent};
               cursor:pointer;color:{tokens.accent};font-size:11px;
               border-radius:6px;padding:4px 12px;width:100%;
               text-transform:uppercase;letter-spacing:.07em;font-weight:600;">
        &larr; Back
      </button>
    </div>"""

    # ── Full card HTML ────────────────────────────────────────────────────────
    card_html = f"""
    <!DOCTYPE html><html><head>
    <style>
      * {{ box-sizing:border-box; }}
      body {{
        margin:0;padding:0;
        background:{tokens.bg_surface};
        font-family:{tokens.font_primary};
        color:{tokens.text_primary};
      }}
      .card {{
        background:{tokens.bg_surface};
        border:1px solid {tokens.border};
        border-radius:14px;
        padding:16px 14px;
        min-height:210px;
      }}
      .period-pill {{
        display:inline-block;
        background:rgba(0,212,255,0.12);
        color:{tokens.accent};
        font-size:10px;font-weight:600;
        text-transform:uppercase;letter-spacing:.08em;
        padding:2px 8px;border-radius:20px;
        margin-bottom:8px;
      }}
      .metric-title {{
        font-size:12px;font-weight:600;
        text-transform:uppercase;letter-spacing:.1em;
        color:{tokens.text_muted};
        margin-bottom:4px;
      }}
      .metric-value {{
        font-size:26px;font-weight:700;
        color:{tokens.text_primary};
        letter-spacing:-.5px;
        margin-bottom:12px;
        line-height:1.1;
      }}
      .compare-block {{
        margin-bottom:8px;
      }}
      .compare-row {{
        display:flex;
        align-items:center;
        flex-wrap:wrap;
        gap:5px;
        margin-top:2px;
      }}
      .compare-label {{
        font-size:10px;
        color:{tokens.text_muted};
        text-transform:uppercase;
        letter-spacing:.07em;
        white-space:nowrap;
      }}
      .ref-value {{
        font-size:12px;
        font-weight:700;
        color:{tokens.text_primary};
        white-space:nowrap;
      }}
      .badge {{
        display:inline-flex;align-items:center;gap:3px;
        padding:2px 7px;border-radius:6px;
        font-size:11px;font-weight:600;
        white-space:nowrap;
      }}
      .divider {{
        width:3px;height:3px;border-radius:50%;
        background:{tokens.border};
        display:inline-block;
        margin:0 1px;
      }}
    </style>
    </head><body>
    <div class="card">

      <!-- FRONT -->
      <div id="{front_id}">
        <div class="period-pill">{period_label}</div>
        <div class="metric-title">{title}</div>
        <div class="metric-value">{val_str}</div>
        {compare_html}
        {flip_btn}
      </div>

      <!-- BACK (drivers) -->
      <div id="{back_id}" style="display:none;">
        <div class="period-pill">{period_label}</div>
        <div class="metric-title">{title}</div>
        {drivers_html}
        {back_btn}
      </div>

    </div>
    </body></html>
    """

    stc.html(card_html, height=height, scrolling=False)
