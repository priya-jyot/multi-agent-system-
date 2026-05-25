"""Marketing Strategy Agent — campaigns, branding, positioning."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from tools.analytics import parse_swot_text
from tools.groq_client import format_prompt


class StrategyAgent(BaseAgent):
  name = "strategy"
  display_name = "Marketing Strategy Agent"
  description = "Generates campaigns, branding, and marketing plans."

  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    inp = context.get("input", {})
    business = inp.get("business_name", "Unknown")
    industry = inp.get("industry", "General")
    audience = inp.get("target_audience", "General")

    full_context = self._build_context_summary(context)

    # SWOT generation
    swot_prompt = format_prompt(
        "swot",
        business_name=business,
        industry=industry,
        full_context=full_context[:2500],
    )
    swot_text = self._generate(swot_prompt, fallback=self._fallback_swot(business))
    swot = parse_swot_text(swot_text)

    strategy_prompt = format_prompt(
        "strategy",
        business_name=business,
        industry=industry,
        target_audience=audience,
        full_context=full_context[:3000],
    )
    strategy_output = self._generate(
        strategy_prompt,
        fallback=self._fallback_strategy(business, audience),
    )

    recommendations = self._generate(
        f"List 5 actionable recommendations for {business} based on:\n{full_context[:2000]}",
        fallback="1. Validate ICP\n2. Run A/B campaigns\n3. Improve onboarding\n"
        "4. Build referral loop\n5. Monitor competitor moves weekly.",
    )

    return {
        "strategy": strategy_output,
        "marketing_strategy": strategy_output,
        "swot_text": swot_text,
        "swot": swot,
        "recommendations": recommendations,
        "output": strategy_output,
    }

  def _build_context_summary(self, context: dict) -> str:
    parts = []
    for key in (
        "market_research", "competitor_analysis", "customer_sentiment",
        "trend_forecast", "battle_card",
    ):
      val = context.get(key, "")
      if val:
        parts.append(f"### {key}\n{str(val)[:800]}")
    return "\n\n".join(parts)

  def _fallback_swot(self, business: str) -> str:
    return f"""Strengths:
- Innovative product ({business})
- Agile team

Weaknesses:
- Limited brand awareness
- Early-stage distribution

Opportunities:
- Growing market demand
- Digital channel expansion

Threats:
- Established competitors
- Economic uncertainty
"""

  def _fallback_strategy(self, business: str, audience: str) -> str:
    return f"""## Marketing Strategy (Offline)

**Positioning:** {business} — the smart choice for {audience}.

### Campaigns
1. Launch awareness campaign on LinkedIn and Instagram
2. Referral program for early adopters
3. Educational webinar series

### Channels
- Content marketing (blog, SEO)
- Email nurture sequences
- Community building (Discord/Slack)
"""
