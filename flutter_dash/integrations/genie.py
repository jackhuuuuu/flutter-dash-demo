# flutter_dash/integrations/genie.py
"""
Genie AI integration — chat queries and stored commentary.

Genie is Databricks' natural-language-to-SQL assistant.  This module
provides two usage patterns:

1. **Live chat** — send a question to a Genie Space and get an answer
   back in real time.  Rendered as a chat panel in the dashboard.

2. **Stored answers** — pre-generated commentary stored in a Unity
   Catalog table, displayed as styled AI commentary blocks alongside
   each dashboard section.

All methods are **safe no-ops** when Genie is not configured — they
return placeholder text or render a "not configured" message.  This
means dashboards work fine in local/CSV mode without Databricks.

Usage:
    from flutter_dash.integrations.genie import GenieClient

    genie = GenieClient(space_id="abc123")

    # Live chat (Phase 4 stub — will call Genie API when available)
    answer = genie.ask("What drove the revenue increase this week?")

    # Stored answers (read from Unity Catalog table)
    commentary = genie.get_stored_answers(
        catalog="flutter_analytics",
        schema="gold",
        table="genie_commentary",
        section_filter="kpi",
    )

    # Render in Streamlit
    genie.render_commentary(answer)
    genie.render_chat()
"""

from __future__ import annotations

import logging
from typing import Optional

import streamlit as st

from flutter_dash.integrations.databricks import DatabricksConnector
from flutter_dash.theme import get_active_theme

logger = logging.getLogger(__name__)


class GenieClient:
    """
    Interface to Databricks Genie AI for dashboard commentary.

    Parameters
    ----------
    space_id : str, optional
        Genie Space ID for live chat queries.  Leave empty to disable
        live chat (stored answers still work).
    connector : DatabricksConnector, optional
        An existing connector for reading stored answers.  If not
        provided, one is created with default env-var credentials.
    """

    def __init__(
        self,
        space_id: str = "",
        connector: Optional[DatabricksConnector] = None,
    ):
        self.space_id = space_id
        self.connector = connector or DatabricksConnector()

    # ── Status helpers ────────────────────────────────────────────────────

    def is_chat_available(self) -> bool:
        """Return ``True`` if live chat is configured (space ID + credentials)."""
        return bool(self.space_id) and self.connector.is_available()

    def is_stored_available(self) -> bool:
        """Return ``True`` if the Databricks connector can read stored answers."""
        return self.connector.is_available()

    # ═════════════════════════════════════════════════════════════════════
    # 1. LIVE CHAT — ask Genie a question
    # ═════════════════════════════════════════════════════════════════════

    def ask(self, question: str) -> str:
        """
        Send a natural-language question to the Genie Space and return
        the answer text.

        .. note::
            This is a **stub** for now.  The actual Genie Conversation
            API (``/api/2.0/genie/spaces/{space_id}/conversations``)
            will be wired in when the Genie Space is set up.

        Parameters
        ----------
        question : str
            The question to ask, e.g. "What drove revenue growth this week?"

        Returns
        -------
        str
            The answer text, or a placeholder if Genie is not available.
        """
        if not self.is_chat_available():
            logger.info("Genie chat not configured — returning placeholder")
            return (
                "_Genie AI is not configured yet.  "
                "Set up a Genie Space and pass its ID to GenieClient._"
            )

        # ── STUB — replace with actual Genie API call ─────────────────
        # When the Genie Space is ready, this will:
        #   1. POST to /api/2.0/genie/spaces/{space_id}/conversations
        #      with {"content": question}
        #   2. Poll for the conversation result
        #   3. Extract the answer text from the response
        #
        # For now, return a placeholder so the UI renders correctly.
        logger.info("Genie ask (stub): %s", question[:80])
        return (
            f"_[Genie stub] Received question: \"{question}\"  \n"
            "Actual Genie API integration coming soon._"
        )

    # ═════════════════════════════════════════════════════════════════════
    # 2. STORED ANSWERS — read pre-generated commentary
    # ═════════════════════════════════════════════════════════════════════

    def get_stored_answers(
        self,
        catalog: str,
        schema: str,
        table: str,
        section_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Read pre-generated Genie commentary from a Unity Catalog table.

        The table should have at least these columns:
          - ``section`` (str) — which dashboard section this applies to
            (e.g. "kpi", "trend", "breakdown")
          - ``commentary`` (str) — the AI-generated text
          - ``generated_at`` (timestamp) — when it was generated

        Parameters
        ----------
        catalog, schema, table : str
            Fully-qualified table location in Unity Catalog.
        section_filter : str, optional
            If provided, only return rows where ``section`` matches.

        Returns
        -------
        list[dict]
            Each dict has keys matching the table columns.
            Returns an empty list if Databricks is not available.
        """
        if not self.is_stored_available():
            logger.info("Databricks not available — no stored answers")
            return []

        fqn = f"`{catalog}`.`{schema}`.`{table}`"
        sql = f"SELECT * FROM {fqn}"
        if section_filter:
            # Parameterised via string formatting with backtick-quoted
            # identifiers.  section_filter is an internal constant (not
            # user input) so this is safe.
            sql += f" WHERE section = '{section_filter}'"
        sql += " ORDER BY generated_at DESC"

        try:
            df = self.connector.query(sql)
            return df.to_dict("records")
        except Exception:
            logger.exception("Failed to read stored Genie answers")
            return []

    # ═════════════════════════════════════════════════════════════════════
    # 3. STREAMLIT RENDERING
    # ═════════════════════════════════════════════════════════════════════

    def render_commentary(
        self,
        text: str,
        title: str = "AI Commentary",
        icon: str = "🤖",
    ) -> None:
        """
        Render a styled AI commentary block in Streamlit.

        Parameters
        ----------
        text : str
            The commentary text (supports Markdown).
        title : str
            Header text for the block.
        icon : str
            Emoji icon shown next to the title.
        """
        tokens = get_active_theme()
        st.markdown(
            f"""
            <div style="
                background: {tokens.bg_elevated};
                border: 1px solid {tokens.border};
                border-left: 3px solid {tokens.accent};
                border-radius: 8px;
                padding: 16px 20px;
                margin: 8px 0 16px;
            ">
                <div style="
                    color: {tokens.accent};
                    font-size: 13px;
                    font-weight: 600;
                    margin-bottom: 8px;
                ">
                    {icon} {title}
                </div>
                <div style="
                    color: {tokens.text_primary};
                    font-size: 13px;
                    line-height: 1.6;
                ">
                    {text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_chat(self) -> None:
        """
        Render a simple Genie chat panel with input + response.

        Uses ``st.session_state`` to persist the conversation.
        Shows a "not configured" message if Genie is not available.
        """
        tokens = get_active_theme()

        st.markdown(
            f"""
            <div style="
                color: {tokens.accent};
                font-size: 15px;
                font-weight: 600;
                margin: 16px 0 8px;
            ">
                🤖 Ask Genie
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not self.is_chat_available():
            st.info(
                "Genie AI chat is not configured.  "
                "Set up a Genie Space and provide the Space ID to enable this feature.",
                icon="ℹ️",
            )
            return

        # Chat input
        question = st.text_input(
            "Ask a question about the data",
            placeholder="e.g. What drove revenue growth this week?",
            key="genie_chat_input",
        )

        if question:
            with st.spinner("Asking Genie..."):
                answer = self.ask(question)
            self.render_commentary(answer, title="Genie Response")
