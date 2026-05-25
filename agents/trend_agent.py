"""Trend Forecasting Agent — emerging trends and market direction."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from tools.groq_client import format_prompt


class TrendAgent(BaseAgent):
  name = "trend"
  display_name = "Trend Forecasting Agent"
  description = "Detects trends and forecasts market direction."

  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    inp = context.get("input", {})
    business = inp.get("business_name", "Unknown")
    industry = inp.get("industry", "General")
    market_context = context.get("market_context", "")
    web = context.get("web_data", {})
    trend_data = web.get("news_summary", "")

    prompt = format_prompt(
        "trend",
        business_name=business,
        industry=industry,
        market_context=market_context[:2000],
        trend_data=trend_data[:2000],
    )
    output = self._generate(
        prompt,
        fallback=self._fallback_trends(industry),
    )

    return {
        "trend": output,
        "trend_forecast": output,
        "output": output,
    }

  def _fallback_trends(self, industry: str) -> str:
    return f"""## Trend Forecast (Offline)

**Industry:** {industry}

### Emerging Trends
1. AI-assisted personalization in marketing
2. Privacy-first analytics and first-party data
3. Short-form video and community-led growth
4. Sustainability and ethical brand positioning

### 6-12 Month Outlook
Continued consolidation with room for niche innovators. Invest in content and retention.
"""
