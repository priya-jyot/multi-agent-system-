"""Dashboard page — metrics, recent research, insights."""

from __future__ import annotations

import streamlit as st

from config import APP_TITLE
from tools.file_handler import list_reports, load_research_history
from ui.charts import trend_line


def render_dashboard():
  st.title(f"{APP_TITLE} Dashboard")
  st.markdown(
      '<p class="tagline">Real-time marketing intelligence powered by collaborative AI agents.</p>',
      unsafe_allow_html=True,
  )

  reports = list_reports()
  history = load_research_history()
  ctx = st.session_state.get("last_research", {})

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Total Reports", len(reports))
  c2.metric("Research Sessions", len(history))
  c3.metric(
      "Active Agents",
      len([a for a in ctx.get("agent_timeline", []) if a.get("status") == "completed"]) or 6,
  )
  sentiment = ctx.get("sentiment", {}).get("summary", {})
  c4.metric(
      "Avg Sentiment",
      f"{sentiment.get('avg_compound', 0):.2f}" if sentiment else "—",
  )

  st.divider()
  left, right = st.columns([2, 1])

  with left:
    st.subheader("Recent Research")
    if history:
      for item in history[:5]:
        inp = item.get("input", {})
        st.markdown(
            f'<div class="agent-card">'
            f'<h4>{inp.get("business_name", "Unknown")}</h4>'
            f'<span style="color:#94a3b8">{inp.get("industry", "")} · '
            f'{item.get("timestamp", "")[:10]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
      st.info("No research yet. Go to **Research Workspace** to start.")

  with right:
    st.subheader("AI Insights")
    if ctx.get("market_research"):
      st.markdown(
          f'<div class="insight-box">{ctx["market_research"][:400]}...</div>',
          unsafe_allow_html=True,
      )
    else:
      st.markdown(
          '<div class="insight-box">Start a research session to see AI-generated insights here.</div>',
          unsafe_allow_html=True,
      )

  st.subheader("Trend Summary")
  st.plotly_chart(trend_line(), use_container_width=True)

  if reports:
    st.subheader("Latest Reports")
    for r in reports[:3]:
      st.caption(f"📄 {r['business_name']} — {r['id']}")
