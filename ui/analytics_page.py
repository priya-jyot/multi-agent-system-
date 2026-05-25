"""Analytics page."""

from __future__ import annotations

import streamlit as st

from ui.charts import render_analytics_charts


def render_analytics():
  st.title("Analytics")
  st.caption("Sentiment, competitor, trend, and SWOT visualizations.")

  ctx = st.session_state.get("last_research", {})
  if not ctx:
    st.info("Complete a research session to populate analytics.")
  render_analytics_charts(ctx)
