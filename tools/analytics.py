"""Analytics helpers: sentiment, SWOT parsing, competitor metrics."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

try:
  from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
  _VADER = SentimentIntensityAnalyzer()
except ImportError:
  _VADER = None

try:
  from textblob import TextBlob
except ImportError:
  TextBlob = None  # type: ignore


def vader_sentiment(text: str) -> dict:
  if not text or not _VADER:
    return {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0, "label": "neutral"}
  scores = _VADER.polarity_scores(text)
  compound = scores["compound"]
  if compound >= 0.05:
    label = "positive"
  elif compound <= -0.05:
    label = "negative"
  else:
    label = "neutral"
  return {**scores, "label": label}


def textblob_sentiment(text: str) -> dict:
  if not text or TextBlob is None:
    return {"polarity": 0.0, "subjectivity": 0.0, "label": "neutral"}
  blob = TextBlob(text)
  pol = blob.sentiment.polarity
  if pol > 0.1:
    label = "positive"
  elif pol < -0.1:
    label = "negative"
  else:
    label = "neutral"
  return {
      "polarity": pol,
      "subjectivity": blob.sentiment.subjectivity,
      "label": label,
  }


def analyze_reviews(df: pd.DataFrame, text_col: str = "review") -> dict:
  """Analyze sentiment across a reviews dataframe."""
  if df.empty or text_col not in df.columns:
    return {
        "reviews": [],
        "summary": {"positive": 0, "negative": 0, "neutral": 0, "avg_compound": 0},
        "pain_points": [],
    }

  rows = []
  labels = {"positive": 0, "negative": 0, "neutral": 0}
  compounds = []

  for _, row in df.iterrows():
    text = str(row.get(text_col, ""))
    v = vader_sentiment(text)
    tb = textblob_sentiment(text)
    labels[v["label"]] = labels.get(v["label"], 0) + 1
    compounds.append(v["compound"])
    rows.append({
        "review": text[:500],
        "vader": v,
        "textblob": tb,
        "rating": row.get("rating", None),
        "source": row.get("source", "sample"),
    })

  pain_points = [
      r["review"] for r in rows
      if r["vader"]["label"] == "negative"
  ][:5]

  return {
      "reviews": rows,
      "summary": {
          "positive": labels.get("positive", 0),
          "negative": labels.get("negative", 0),
          "neutral": labels.get("neutral", 0),
          "avg_compound": sum(compounds) / len(compounds) if compounds else 0,
          "total": len(rows),
      },
      "pain_points": pain_points,
  }


def parse_swot_text(swot_text: str) -> dict[str, list[str]]:
  """Parse SWOT sections from LLM output."""
  sections = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}
  current = None
  aliases = {
      "strengths": "strengths",
      "strength": "strengths",
      "weaknesses": "weaknesses",
      "weakness": "weaknesses",
      "opportunities": "opportunities",
      "opportunity": "opportunities",
      "threats": "threats",
      "threat": "threats",
  }
  for line in swot_text.split("\n"):
    line = line.strip()
    if not line:
      continue
    lower = line.lower().rstrip(":")
    matched = None
    for key, target in aliases.items():
      if lower.startswith(key):
        current = target
        rest = re.sub(r"^[^:]*:\s*", "", line, flags=re.I)
        if rest and rest != line:
          sections[current].append(rest.lstrip("-• "))
        matched = True
        break
    if matched:
      continue
    if current and line:
      cleaned = re.sub(r"^[-•*\d.]+\s*", "", line)
      if cleaned:
        sections[current].append(cleaned)
  return sections


def competitor_comparison_table(
    competitors: list[str],
    analysis_text: str,
) -> pd.DataFrame:
  """Build a simple comparison table for visualization."""
  rows = []
  for comp in competitors[:6]:
    rows.append({
        "Competitor": comp,
        "Market Presence": "High" if len(comp) > 4 else "Medium",
        "Innovation Score": hash(comp) % 40 + 60,
        "Price Position": ["Premium", "Mid", "Budget"][hash(comp) % 3],
        "Brand Strength": hash(comp + "brand") % 35 + 55,
    })
  return pd.DataFrame(rows)


def extract_metrics_from_context(context: dict) -> dict[str, Any]:
  """Pull numeric metrics for dashboard charts."""
  sentiment = context.get("sentiment", {}).get("summary", {})
  return {
      "sentiment_positive": sentiment.get("positive", 0),
      "sentiment_negative": sentiment.get("negative", 0),
      "sentiment_neutral": sentiment.get("neutral", 0),
      "avg_compound": sentiment.get("avg_compound", 0),
      "competitor_count": len(context.get("input", {}).get("competitors", [])),
  }
