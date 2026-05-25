"""Report Viewer page — view and download reports."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import REPORTS_DIR
from tools.file_handler import list_reports, load_report


def render_reports():
  st.title("Report Viewer")
  st.caption("View and export marketing intelligence reports.")

  reports = list_reports()
  ctx = st.session_state.get("last_research", {})

  if ctx.get("report_id"):
    default_id = ctx["report_id"]
  elif reports:
    default_id = reports[0]["id"]
  else:
    default_id = None

  if not reports and not ctx.get("full_report"):
    st.info("No reports yet. Run research from the Workspace.")
    return

  options = [r["id"] for r in reports] or ([default_id] if default_id else [])
  selected = st.selectbox("Select Report", options, index=0 if options else None)

  report_data = load_report(selected) if selected else None
  full_text = ""

  if report_data:
    full_text = report_data.get("full_text", "")
    inp = report_data.get("input", {})
    st.markdown(f"**Business:** {inp.get('business_name', 'N/A')} · **Industry:** {inp.get('industry', 'N/A')}")
  elif ctx.get("full_report"):
    full_text = ctx["full_report"]
    selected = ctx.get("report_id", "latest")

  if full_text:
    st.text_area("Report Content", full_text, height=500)

    c1, c2 = st.columns(2)
    txt_path = REPORTS_DIR / f"{selected}.txt"
    pdf_path = REPORTS_DIR / f"{selected}.pdf"

    if txt_path.exists():
      c1.download_button(
          "Download TXT",
          txt_path.read_text(encoding="utf-8"),
          file_name=f"{selected}.txt",
          mime="text/plain",
          use_container_width=True,
      )
    if pdf_path.exists():
      c2.download_button(
          "Download PDF",
          pdf_path.read_bytes(),
          file_name=f"{selected}.pdf",
          mime="application/pdf",
          use_container_width=True,
      )
    else:
      c2.caption("PDF will be generated after research completes.")

    if report_data and report_data.get("sections"):
      st.divider()
      st.subheader("Sections")
      for title, content in report_data["sections"].items():
        if content:
          with st.expander(title.replace("_", " ").title()):
            st.markdown(str(content))
  else:
    st.warning("Report file not found.")
