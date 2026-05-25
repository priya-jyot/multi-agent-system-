"""PDF report export using FPDF."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fpdf import FPDF

from config import REPORTS_DIR


class ReportPDF(FPDF):
  def header(self):
    self.set_font("Helvetica", "B", 14)
    self.cell(0, 10, "MarketMind AI - Marketing Intelligence Report", ln=True, align="C")
    self.ln(4)

  def footer(self):
    self.set_y(-15)
    self.set_font("Helvetica", "I", 8)
    self.cell(0, 10, f"Page {self.page_no()}", align="C")


def export_pdf(report_id: str, content: str, title: str = "Report") -> Optional[Path]:
  """Export report text to PDF."""
  try:
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)

    for line in content.split("\n"):
      line = line.replace("\t", "    ")
      # Handle markdown-style headers
      if line.startswith("## "):
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 8, line[3:].strip())
        pdf.set_font("Helvetica", "", 10)
      elif line.startswith("="):
        continue
      else:
        safe = line.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe)

    path = REPORTS_DIR / f"{report_id}.pdf"
    pdf.output(str(path))
    return path
  except Exception:
    return None
