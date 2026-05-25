"""Report Generation Agent — combines outputs, TXT/PDF export."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from agents.base_agent import BaseAgent
from tools.file_handler import save_report_json, save_report_text
from tools.groq_client import format_prompt
from tools.pdf_export import export_pdf
from tools.summarizer import combine_sections


class ReportAgent(BaseAgent):
  name = "report"
  display_name = "Report Generation Agent"
  description = "Compiles final intelligence report."

  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    inp = context.get("input", {})
    business = inp.get("business_name", "Business")
    research_id = context.get("research_id", datetime.now().strftime("%Y%m%d_%H%M%S"))

    full_context = self._full_context(context)

    exec_prompt = format_prompt(
        "report_executive",
        business_name=business,
        full_context=full_context[:3500],
    )
    executive = self._generate(
        exec_prompt,
        fallback=f"Executive Summary: {business} shows strong potential in "
        f"{inp.get('industry', 'its market')} with opportunities in "
        f"{inp.get('target_audience', 'target segments')}.",
    )

    swot = context.get("swot_text", context.get("swot", ""))
    if isinstance(swot, dict):
      swot = self._format_swot_dict(swot)

    sections = {
        "executive_summary": executive,
        "market_overview": str(context.get("market_research", "")),
        "competitor_analysis": str(context.get("competitor_analysis", "")),
        "customer_sentiment": str(context.get("customer_sentiment", "")),
        "swot_analysis": str(swot),
        "trend_forecast": str(context.get("trend_forecast", "")),
        "marketing_strategy": str(context.get("marketing_strategy", "")),
        "recommendations": str(context.get("recommendations", "")),
        "future_opportunities": self._extract_opportunities(context),
    }

    full_report = combine_sections(sections)
    if context.get("battle_card"):
      full_report += f"\n\n## Competitor Battle Card\n\n{context['battle_card']}\n"

    report_data = {
        "id": research_id,
        "timestamp": datetime.now().isoformat(),
        "input": inp,
        "sections": sections,
        "full_text": full_report,
        "agents_used": context.get("agent_timeline", []),
    }

    save_report_text(research_id, full_report)
    save_report_json(research_id, report_data)
    pdf_path = export_pdf(research_id, full_report, title=f"{business} Intelligence Report")

    return {
        "report": report_data,
        "full_report": full_report,
        "report_id": research_id,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "output": full_report[:2000],
    }

  def _full_context(self, context: dict) -> str:
    keys = [
        "market_research", "competitor_analysis", "customer_sentiment",
        "trend_forecast", "marketing_strategy", "battle_card",
    ]
    return "\n".join(f"{k}: {str(context.get(k, ''))[:500]}" for k in keys if context.get(k))

  def _format_swot_dict(self, swot: dict) -> str:
    lines = []
    for title, key in [
        ("Strengths", "strengths"),
        ("Weaknesses", "weaknesses"),
        ("Opportunities", "opportunities"),
        ("Threats", "threats"),
    ]:
      items = swot.get(key, [])
      lines.append(f"{title}:")
      for item in items:
        lines.append(f"  - {item}")
    return "\n".join(lines)

  def _extract_opportunities(self, context: dict) -> str:
    opp = ""
    swot = context.get("swot", {})
    if isinstance(swot, dict) and swot.get("opportunities"):
      opp = "\n".join(f"- {o}" for o in swot["opportunities"])
    trend = context.get("trend_forecast", "")
    if not opp and trend:
      return f"Based on trend analysis:\n{str(trend)[:800]}"
    return opp or "Explore adjacent markets and partnership channels."
