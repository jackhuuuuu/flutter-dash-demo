# flutter_dash/components/sidebar.py
"""
SidebarBuilder — composable sidebar for any dashboard.

Instead of hardcoding sidebar layout, use SidebarBuilder to add
widgets one by one. Each dashboard picks the widgets it needs.

Available widgets:
  - add_header()          → branded title with subtitle
  - add_theme_toggle()    → light/dark mode switch
  - add_period_picker()   → Yesterday / WTD / MTD selector with auto dates
  - add_multiselect()     → multi-select filter (Brand, Product, etc.)
  - add_metric_picker()   → single-select for primary chart metric
  - add_grouping_picker() → single-select for chart dimension grouping
  - add_divider()         → horizontal line separator
  - add_footer()          → small text at the bottom

Usage:
    sb = SidebarBuilder(st)
    sb.add_header("My Dashboard", "Performance Report")
    sb.add_theme_toggle()
    sb.add_period_picker()
    sb.add_multiselect("Brand", all_brands)
    sb.add_metric_picker(["Revenue", "Stakes", "Margin %"])
    sb.add_grouping_picker(["Brand", "Product"])
    selections = sb.render()
"""

import streamlit as st
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from flutter_dash.theme import get_active_theme
from flutter_dash.theme.tokens import ThemeTokens
from flutter_dash.data.date_helpers import get_period_dates


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

    def add_theme_toggle(self) -> "SidebarBuilder":
        """Add a light/dark theme toggle right after the header."""
        self._widgets.append(("theme_toggle", {}))
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

    def add_grouping_picker(
        self,
        options: List[str] = None,
        label: str = "Chart Grouping",
    ) -> "SidebarBuilder":
        """
        Add a single-select dropdown for chart dimension grouping.

        Controls which dimension (e.g. Brand or Product) is used to
        group bar charts and pie charts. The selected value is returned
        in results as "grouping".
        """
        if options is None:
            options = ["Brand", "Product"]
        self._widgets.append(("grouping_picker", {
            "label": label,
            "options": options,
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

                elif widget_type == "theme_toggle":
                    _is_dark = self._st.session_state.get("theme") == "dark"
                    _icon = "☀️" if _is_dark else "🌙"
                    if self._st.button(
                        _icon,
                        key="theme_toggle",
                    ):
                        self._st.session_state.theme = (
                            "light" if _is_dark else "dark"
                        )
                        self._st.rerun()

                elif widget_type == "period":
                    period = self._st.selectbox(
                        "Period",
                        config["options"],
                        index=config["default_index"],
                    )
                    max_d = config.get("max_date") or date.today()
                    start, end = get_period_dates(max_d, period)
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

                elif widget_type == "grouping_picker":
                    selected = self._st.selectbox(
                        config["label"],
                        config["options"],
                    )
                    results["grouping"] = selected.lower()

                elif widget_type == "divider":
                    self._st.markdown("---")

                elif widget_type == "footer":
                    self._st.markdown(
                        f'<p style="color:{t.text_muted};font-size:10px;">'
                        f'{config["text"]}</p>',
                        unsafe_allow_html=True,
                    )

        return results
