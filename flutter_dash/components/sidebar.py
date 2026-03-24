# flutter_dash/components/sidebar.py
"""
SidebarBuilder — composable sidebar for any dashboard.

Instead of hardcoding sidebar layout, use SidebarBuilder to add
widgets one by one. Each dashboard picks the widgets it needs.

Usage:
    sb = SidebarBuilder(st, tokens)
    sb.add_header("My Dashboard", "Performance Report")
    sb.add_period_picker()
    sb.add_multiselect("Brand", all_brands)
    sb.add_metric_picker({"Revenue": ..., "Margin": ...})
    sb.add_footer(f"Data as of {max_date}")
    selections = sb.render()

    # selections is a dict:
    # {
    #   "period": "MTD",
    #   "period_start": date(...),
    #   "period_end": date(...),
    #   "Brand": ["Brand A", "Brand B"],
    #   "metric": "Revenue",
    # }
"""

import streamlit as st
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import ThemeTokens


class SidebarBuilder:
    """
    Builds a composable sidebar for a Streamlit dashboard.

    Add widgets in order, then call render() to display them and
    get back a dict of all selected values.
    """

    def __init__(
        self,
        st_module=None,
        tokens: Optional[ThemeTokens] = None,
    ):
        """
        Parameters
        ----------
        st_module : streamlit
            The streamlit module. If None, uses the default import.
        tokens : ThemeTokens, optional
            Theme palette for styled elements. Defaults to active theme.
        """
        self._st = st_module or st
        self._tokens = tokens or get_active_theme()
        # Ordered list of (widget_type, widget_config) to render
        self._widgets: list = []
        self._results: Dict[str, Any] = {}

    def add_header(self, title: str, subtitle: str = "") -> "SidebarBuilder":
        """Add a branded header at the top of the sidebar."""
        self._widgets.append(("header", {"title": title, "subtitle": subtitle}))
        return self

    def add_period_picker(
        self,
        options: List[str] = None,
        default_index: int = 2,
        max_date: Optional[date] = None,
    ) -> "SidebarBuilder":
        """
        Add a period selector (Yesterday, WTD, MTD, etc.).

        Automatically calculates start/end dates based on the selection.
        The calculated dates are returned in the results dict as
        "period", "period_start", "period_end".
        """
        if options is None:
            options = ["Yesterday", "WTD", "MTD"]
        self._widgets.append(("period", {
            "options": options,
            "default_index": default_index,
            "max_date": max_date,
        }))
        return self

    def add_multiselect(
        self,
        label: str,
        options: List[str],
        default: Optional[List[str]] = None,
        placeholder: Optional[str] = None,
    ) -> "SidebarBuilder":
        """
        Add a multiselect filter (e.g. Brand, Product, Region).

        If the user clears all selections, it defaults back to "all".
        """
        if default is None:
            default = list(options)
        if placeholder is None:
            placeholder = f"All {label}s"
        self._widgets.append(("multiselect", {
            "label": label,
            "options": options,
            "default": default,
            "placeholder": placeholder,
        }))
        return self

    def add_metric_picker(
        self,
        metric_labels: List[str],
        label: str = "Primary Metric (Charts)",
    ) -> "SidebarBuilder":
        """
        Add a single-select dropdown for choosing the primary metric.

        The selected label is returned in results as "metric".
        """
        self._widgets.append(("metric_picker", {
            "label": label,
            "options": metric_labels,
        }))
        return self

    def add_divider(self) -> "SidebarBuilder":
        """Add a horizontal divider line."""
        self._widgets.append(("divider", {}))
        return self

    def add_footer(self, text: str) -> "SidebarBuilder":
        """Add footer text at the bottom (e.g. 'Data as of 24 Mar 2026')."""
        self._widgets.append(("footer", {"text": text}))
        return self

    def render(self) -> Dict[str, Any]:
        """
        Render all widgets in the sidebar and return selections.

        Returns
        -------
        dict
            Keys depend on what widgets were added:
            - "period", "period_start", "period_end" (from period picker)
            - filter labels like "Brand", "Product" (from multiselects)
            - "metric" (from metric picker)
        """
        t = self._tokens
        results = {}

        with self._st.sidebar:
            for widget_type, config in self._widgets:
                if widget_type == "header":
                    self._st.markdown(
                        f"""
                        <div style="padding:16px 0 24px;">
                          <h1 style="color:{t.accent};font-size:22px;
                                     font-weight:700;margin:0;">
                            📊 {config['title']}
                          </h1>
                          <p style="color:{t.text_muted};font-size:12px;
                                    margin:4px 0 0;">
                            {config['subtitle']}
                          </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                elif widget_type == "period":
                    period = self._st.selectbox(
                        "Period",
                        config["options"],
                        index=config["default_index"],
                    )
                    max_d = config.get("max_date") or date.today()
                    start, end = self._calc_period_dates(period, max_d)
                    results["period"] = period
                    results["period_start"] = start
                    results["period_end"] = end

                    self._st.markdown(
                        f'<p style="color:{t.text_muted};font-size:11px;'
                        f'margin:-8px 0 16px;">'
                        f'{start.strftime("%d %b %Y")} → '
                        f'{end.strftime("%d %b %Y")}</p>',
                        unsafe_allow_html=True,
                    )

                elif widget_type == "multiselect":
                    selected = self._st.multiselect(
                        config["label"],
                        config["options"],
                        default=config["default"],
                        placeholder=config["placeholder"],
                    )
                    # If user clears selection, default back to all
                    if not selected:
                        selected = list(config["options"])
                    results[config["label"]] = selected

                elif widget_type == "metric_picker":
                    selected = self._st.selectbox(
                        config["label"],
                        config["options"],
                    )
                    results["metric"] = selected

                elif widget_type == "divider":
                    self._st.markdown("---")

                elif widget_type == "footer":
                    self._st.markdown(
                        f'<p style="color:{t.text_muted};font-size:10px;">'
                        f'{config["text"]}</p>',
                        unsafe_allow_html=True,
                    )

        return results

    # ── Internal: calculate period dates ──────────────────────────────────────
    @staticmethod
    def _calc_period_dates(period: str, max_date: date) -> Tuple[date, date]:
        """
        Convert a period label into start/end dates.

        Supports: Yesterday, WTD (week-to-date), MTD (month-to-date).
        Can be extended with QTD, YTD, etc.
        """
        if period == "Yesterday":
            d = max_date - timedelta(days=1)
            return d, d
        elif period == "WTD":
            start = max_date - timedelta(days=max_date.weekday())
            return start, max_date
        elif period == "QTD":
            # Quarter start: month 1, 4, 7, or 10
            q_month = ((max_date.month - 1) // 3) * 3 + 1
            return max_date.replace(month=q_month, day=1), max_date
        elif period == "YTD":
            return max_date.replace(month=1, day=1), max_date
        else:
            # Default: MTD
            return max_date.replace(day=1), max_date
