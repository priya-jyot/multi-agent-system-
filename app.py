"""
MarketMind AI — Multi-Agent Marketing Research & Competitive Intelligence Platform

Run: streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import streamlit as st

from config import APP_TITLE
from ui.analytics_page import render_analytics
from ui.dashboard import render_dashboard
from ui.monitor import render_monitor
from ui.reports_page import render_reports
from ui.sidebar import render_sidebar
from ui.theme import apply_theme
from ui.workspace import render_workspace

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session defaults
_defaults = {
    "last_research": {},
    "research_logs": [],
    "active_agent": None,
    "groq_model": "llama-3.3-70b-versatile",
}
for k, v in _defaults.items():
  if k not in st.session_state:
    st.session_state[k] = v

apply_theme()
page = render_sidebar()

if page == "dashboard":
  render_dashboard()
elif page == "workspace":
  render_workspace()
elif page == "monitor":
  render_monitor()
elif page == "analytics":
  render_analytics()
elif page == "reports":
  render_reports()
else:
  render_dashboard()
