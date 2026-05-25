"""Research Workspace page."""

from __future__ import annotations

import streamlit as st

from config import REPORTS_DIR
from workflows.research_pipeline import build_input, run_research, run_strategy_pipeline


def render_workspace():
  st.title("Research Workspace")
  st.caption("Configure your business context and launch the multi-agent research pipeline.")

  with st.form("research_form"):
    c1, c2 = st.columns(2)
    with c1:
      business = st.text_input("Product / Business Name *", placeholder="EcoSip Smart Bottle")
      industry = st.text_input("Industry *", placeholder="Consumer Health Tech")
    with c2:
      audience = st.text_input("Target Audience", placeholder="Health-conscious millennials")
      competitors = st.text_input(
          "Competitors (comma-separated)",
          placeholder="Hydro Flask, Yeti, Stanley",
      )

    uploaded = st.file_uploader(
        "Upload customer reviews (CSV with 'review' column)",
        type=["csv"],
    )
    submitted = st.form_submit_button("Start Full Research", use_container_width=True)

  col_a, col_b, col_c = st.columns(3)
  strategy_only = col_b.button("Generate Strategy Only", use_container_width=True)
  export_clicked = col_c.button("Export Report", use_container_width=True)

  if export_clicked:
    _export_latest_report()

  if submitted:
    _run_pipeline(business, industry, audience, competitors, uploaded, full=True)
  elif strategy_only:
    _run_pipeline(business, industry, audience, competitors, uploaded, full=False)


def _run_pipeline(business, industry, audience, competitors, uploaded, full: bool):
  if not business or not industry:
    st.warning("Please enter business name and industry.")
    return

  input_data = build_input(business, industry, audience, competitors)
  model = st.session_state.get("groq_model")
  progress = st.progress(0)
  log_area = st.empty()
  logs = []

  def on_step(key, name, current, total):
    progress.progress(current / total)
    st.session_state["active_agent"] = name

  def on_log(msg):
    logs.append(msg)
    log_area.code("\n".join(logs[-8:]))

  with st.spinner("AI agents collaborating..."):
    if full:
      result, err = run_research(
          input_data,
          uploaded_reviews=uploaded,
          model=model,
          on_step=on_step,
          on_log=on_log,
      )
    else:
      result, err = run_strategy_pipeline(input_data, model=model)

  st.session_state["last_research"] = result
  st.session_state["research_logs"] = logs
  progress.progress(1.0)

  if err:
    st.warning(f"Note: {err} — Fallback content may have been used.")

  if result.get("full_report") or result.get("report"):
    st.success(f"Research complete! Report ID: {result.get('report_id', 'N/A')}")
    with st.expander("Preview Executive Summary", expanded=True):
      sections = result.get("report", {}).get("sections", {})
      st.write(sections.get("executive_summary", result.get("full_report", "")[:1500]))
  else:
    st.error("Research finished but no report was generated. Check logs.")


def _export_latest_report():
  ctx = st.session_state.get("last_research", {})
  report_id = ctx.get("report_id")
  if not report_id:
    st.warning("No report to export. Run research first.")
    return
  txt_path = REPORTS_DIR / f"{report_id}.txt"
  pdf_path = REPORTS_DIR / f"{report_id}.pdf"
  if txt_path.exists():
    st.download_button(
        "Download TXT",
        txt_path.read_text(encoding="utf-8"),
        file_name=f"{report_id}.txt",
        key="ws_txt",
    )
  if pdf_path.exists():
    st.download_button(
        "Download PDF",
        pdf_path.read_bytes(),
        file_name=f"{report_id}.pdf",
        key="ws_pdf",
    )
  if not txt_path.exists() and not pdf_path.exists():
    st.warning("Report files not found. Complete a research run first.")
