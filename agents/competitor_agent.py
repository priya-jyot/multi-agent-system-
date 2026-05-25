"""Competitor Intelligence Agent — battle cards, pricing, SWOT per competitor."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from tools.groq_client import format_prompt


class CompetitorAgent(BaseAgent):
  name = "competitor"
  display_name = "Competitor Intelligence Agent"
  description = "Analyzes competitors, pricing, and battle cards."

  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    inp = context.get("input", {})
    business = inp.get("business_name", "Unknown")
    industry = inp.get("industry", "General")
    competitors = ", ".join(inp.get("competitors", [])) or "Industry leaders"
    market_context = context.get("market_context", context.get("market_research", ""))
    web = context.get("web_data", {})
    web_data = web.get("competitor_summary", "No scraped data")

    prompt = format_prompt(
        "competitor",
        business_name=business,
        industry=industry,
        competitors=competitors,
        market_context=market_context[:2000],
        web_data=web_data[:2000],
    )
    output = self._generate(
        prompt,
        fallback=self._fallback_competitor(inp.get("competitors", [])),
    )

    battle_card = self._generate(
        f"Create a one-page competitor battle card for {business} vs {competitors}. "
        f"Use this analysis:\n{output[:1500]}\n\nFormat: Quick wins, Objections, Differentiators.",
        fallback="Battle card: Emphasize unique value proposition and customer success stories.",
    )

    return {
        "competitor": output,
        "competitor_analysis": output,
        "battle_card": battle_card,
        "output": output,
    }

  def _fallback_competitor(self, competitors: list) -> str:
    names = ", ".join(competitors) if competitors else "major players"
    return f"""## Competitor Analysis (Offline)

**Competitors tracked:** {names}

### Comparison
| Area | Your Product | Competitors |
|------|--------------|-------------|
| Features | Differentiate on UX | Standard feature parity |
| Pricing | Value-based tiers | Mixed freemium/premium |
| Strengths | Agility, support | Brand, scale |
| Weaknesses | Awareness | Legacy complexity |

### Battle Card Tips
- Lead with outcomes, not features
- Prepare pricing objection handlers
"""
