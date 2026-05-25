"""Market Research Agent — industry, audience, opportunities."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from tools.groq_client import format_prompt
from tools.web_scraper import aggregate_web_context


class MarketResearchAgent(BaseAgent):
  name = "market_research"
  display_name = "Market Research Agent"
  description = "Analyzes industry, target audience, and market opportunities."

  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    inp = context.get("input", {})
    business = inp.get("business_name", "Unknown")
    industry = inp.get("industry", "General")
    audience = inp.get("target_audience", "General consumers")
    competitors = ", ".join(inp.get("competitors", []))

    web = context.get("web_data")
    if not web:
      web = aggregate_web_context(industry, inp.get("competitors", []), business)
      context["web_data"] = web

    prompt = format_prompt(
        "market_research",
        business_name=business,
        industry=industry,
        target_audience=audience,
        competitors=competitors or "Not specified",
    )
    prompt += f"\n\nRecent industry news:\n{web.get('news_summary', 'N/A')}"

    output = self._generate(
        prompt,
        fallback=self._fallback_market(business, industry, audience),
    )

    return {
        "market_research": output,
        "output": output,
        "market_context": output,
    }

  def _fallback_market(self, business: str, industry: str, audience: str) -> str:
    return f"""## Market Research Summary (Offline Template)

**Business:** {business}
**Industry:** {industry}
**Target Audience:** {audience}

### Industry Overview
The {industry} sector shows steady growth with increasing digital adoption.

### Opportunities
- Underserved niche segments in {audience}
- Product-led growth and community marketing
- Partnerships with complementary brands

### Market Gaps
- Limited personalized experiences for {audience}
- Fragmented competitor offerings

### Key Findings
Conduct primary research and validate with customer interviews when the Groq API is available.
"""
