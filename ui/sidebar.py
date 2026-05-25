"""Sidebar navigation and Groq API status."""

from __future__ import annotations

import streamlit as st

from config import APP_TAGLINE, APP_TITLE, GROQ_MODEL
from workflows.research_pipeline import check_groq_status


PAGES = {
    "Dashboard": "dashboard",
    "Research Workspace": "workspace",
    "Agent Monitor": "monitor",
    "Analytics": "analytics",
    "Report Viewer": "reports",
}


def render_sidebar() -> str:
  with st.sidebar:
    st.markdown(f"# {APP_TITLE}")
    st.caption(APP_TAGLINE)
    st.divider()

    page = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
        key="nav_page",
    )

    st.divider()
    st.subheader("System Status")
    status = check_groq_status()
    if status["available"]:
      st.success("Groq API: Configured")
    else:
      st.warning("Groq API: Not configured")
      st.caption("Create `.env` with `GROQ_API_KEY` (see README)")

    models = status.get("models") or [GROQ_MODEL]
    default_idx = 0
    if GROQ_MODEL in models:
      default_idx = models.index(GROQ_MODEL)

    model_choice = st.selectbox(
        "LLM Model",
        options=models,
        index=default_idx,
        help="Groq cloud model used by all agents",
    )
    st.session_state["groq_model"] = model_choice

    if status["available"] and st.button("Test Groq connection", use_container_width=True):
      from tools.groq_client import GroqClient
      client = GroqClient(model=model_choice)
      ok, msg = client.test_connection()
      if ok:
        st.success(msg)
      else:
        st.error(msg)

    st.divider()
    st.markdown("**Quick Tips**")
    st.markdown(
        "- Enter product & industry\n"
        "- Add comma-separated competitors\n"
        "- Upload CSV reviews (optional)\n"
        "- Export PDF from Reports"
    )

  return PAGES[page]
