"""Agent Monitor page — timeline, logs, outputs."""

from __future__ import annotations

import streamlit as st

from config import AGENT_LOG, AGENT_NAMES
from config import EXECUTION_LOG


def render_monitor():
  st.title("Agent Monitor")
  st.caption("Track multi-agent execution in real time.")

  ctx = st.session_state.get("last_research", {})
  timeline = ctx.get("agent_timeline", [])

  if not timeline:
    st.info("Run a research session to see agent activity.")
    _show_idle_agents()
    return

  progress = sum(1 for t in timeline if t.get("status") == "completed") / max(len(AGENT_NAMES), 1)
  st.progress(min(progress, 1.0), text=f"Pipeline progress: {int(progress * 100)}%")

  st.subheader("Execution Timeline")
  for i, step in enumerate(timeline):
    status = step.get("status", "idle")
    status_class = f"status-{status}"
    icon = {"completed": "✅", "running": "⏳", "error": "❌"}.get(status, "⚪")
    st.markdown(
        f'<div class="agent-card">'
        f'<h4>{icon} {step.get("display_name", step.get("agent"))}</h4>'
        f'<span class="{status_class}">Status: {status}</span> · '
        f'<span style="color:#94a3b8">Duration: {step.get("duration_ms", 0)} ms</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

  st.subheader("Intermediate Outputs")
  for key in ("market_research", "competitor_analysis", "customer_sentiment", "trend_forecast", "marketing_strategy"):
    val = ctx.get(key)
    if val:
      with st.expander(key.replace("_", " ").title()):
        st.markdown(str(val)[:3000])

  st.subheader("Logs")
  tab1, tab2 = st.tabs(["Agent Logs", "Execution Logs"])
  with tab1:
    _tail_file(AGENT_LOG)
  with tab2:
    _tail_file(EXECUTION_LOG)

  if st.session_state.get("research_logs"):
    with st.expander("Session Logs"):
      st.code("\n".join(st.session_state["research_logs"]))


def _show_idle_agents():
  for key, name in AGENT_NAMES.items():
    st.markdown(
        f'<div class="agent-card"><h4>⚪ {name}</h4>'
        f'<span class="status-idle">Idle — awaiting research</span></div>',
        unsafe_allow_html=True,
    )


def _tail_file(path, lines: int = 40):
  try:
    if path.exists():
      content = path.read_text(encoding="utf-8").splitlines()[-lines:]
      st.code("\n".join(content) or "(empty)")
    else:
      st.caption("No log file yet.")
  except OSError as e:
    st.warning(str(e))
