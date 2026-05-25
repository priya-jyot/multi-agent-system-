"""Sentiment Analysis Agent — reviews, pain points, VADER/TextBlob."""

from __future__ import annotations

from typing import Any

import pandas as pd

from agents.base_agent import BaseAgent
from tools.analytics import analyze_reviews
from tools.file_handler import load_sample_csv
from tools.groq_client import format_prompt


class SentimentAgent(BaseAgent):
  name = "sentiment"
  display_name = "Sentiment Analysis Agent"
  description = "Analyzes customer reviews and sentiment."

  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    inp = context.get("input", {})
    business = inp.get("business_name", "Unknown")

    # Use uploaded reviews or sample data
    df = context.get("reviews_df")
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
      df = load_sample_csv("sample_reviews.csv")
    if not isinstance(df, pd.DataFrame):
      df = pd.DataFrame()

    sentiment_data = analyze_reviews(df, text_col="review")
    context["sentiment"] = sentiment_data

    review_text = "\n".join(
        f"- ({r['vader']['label']}) {r['review'][:200]}"
        for r in sentiment_data.get("reviews", [])[:10]
    )
    scores = sentiment_data.get("summary", {})

    prompt = format_prompt(
        "sentiment",
        business_name=business,
        review_data=review_text or "No reviews available",
        sentiment_scores=str(scores),
    )
    output = self._generate(
        prompt,
        fallback=self._fallback_sentiment(sentiment_data),
    )

    return {
        "sentiment": sentiment_data,
        "sentiment_analysis": output,
        "customer_sentiment": output,
        "output": output,
    }

  def _fallback_sentiment(self, data: dict) -> str:
    s = data.get("summary", {})
    return f"""## Customer Sentiment (Analytics)

- Positive reviews: {s.get('positive', 0)}
- Negative reviews: {s.get('negative', 0)}
- Neutral reviews: {s.get('neutral', 0)}
- Average sentiment score: {s.get('avg_compound', 0):.2f}

### Pain Points
{chr(10).join('- ' + p[:150] for p in data.get('pain_points', [])[:5]) or 'None detected in sample.'}
"""
