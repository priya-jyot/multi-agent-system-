"""Text summarization and report section helpers."""

from __future__ import annotations

import re
from typing import Optional

from tools.groq_client import GroqClient, GroqNotAvailableError


def truncate(text: str, max_len: int = 500) -> str:
  if len(text) <= max_len:
    return text
  return text[: max_len - 3] + "..."


def fallback_summary(text: str, max_sentences: int = 5) -> str:
  """Rule-based summary when LLM unavailable."""
  sentences = re.split(r"(?<=[.!?])\s+", text.strip())
  sentences = [s for s in sentences if len(s) > 20]
  return " ".join(sentences[:max_sentences]) or truncate(text, 400)


def summarize_with_llm(
    text: str,
    focus: str = "key marketing insights",
    client: Optional[GroqClient] = None,
) -> str:
  if not text or len(text) < 100:
    return text or "No content to summarize."
  llm = client or GroqClient()
  prompt = f"""Summarize the following text in 3-5 bullet points focused on {focus}.

Text:
{text[:3000]}

Summary:"""
  try:
    return llm.generate(prompt, temperature=0.3)
  except GroqNotAvailableError:
    return fallback_summary(text)


def combine_sections(sections: dict[str, str]) -> str:
  """Merge report sections into one document."""
  order = [
      ("Executive Summary", "executive_summary"),
      ("Market Overview", "market_overview"),
      ("Competitor Analysis", "competitor_analysis"),
      ("Customer Sentiment", "customer_sentiment"),
      ("SWOT Analysis", "swot_analysis"),
      ("Trend Forecast", "trend_forecast"),
      ("Marketing Strategy", "marketing_strategy"),
      ("Recommendations", "recommendations"),
      ("Future Opportunities", "future_opportunities"),
  ]
  lines = [
      "=" * 60,
      "MARKETMIND AI — MARKETING INTELLIGENCE REPORT",
      "=" * 60,
      "",
  ]
  for title, key in order:
    body = sections.get(key, "").strip()
    if body:
      lines.extend([f"## {title}", "", body, "", ""])
  return "\n".join(lines)
