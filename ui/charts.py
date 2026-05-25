"""Plotly and Matplotlib charts for analytics."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def sentiment_pie(summary: dict) -> go.Figure:
  labels = ["Positive", "Negative", "Neutral"]
  values = [
      summary.get("positive", 0),
      summary.get("negative", 0),
      summary.get("neutral", 0),
  ]
  if sum(values) == 0:
    values = [1, 1, 1]
  fig = px.pie(
      names=labels,
      values=values,
      title="Customer Sentiment Distribution",
      color_discrete_sequence=["#34d399", "#f87171", "#94a3b8"],
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color="#e2e8f0",
      title_font_color="#e2e8f0",
  )
  return fig


def sentiment_bar(reviews: list[dict]) -> go.Figure:
  if not reviews:
    df = pd.DataFrame({"review_id": [1, 2, 3], "compound": [0.2, -0.1, 0.5]})
  else:
    df = pd.DataFrame([
        {"review_id": i + 1, "compound": r["vader"]["compound"]}
        for i, r in enumerate(reviews[:20])
    ])
  fig = px.bar(
      df,
      x="review_id",
      y="compound",
      title="Sentiment Scores by Review",
      color="compound",
      color_continuous_scale=["#f87171", "#94a3b8", "#34d399"],
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color="#e2e8f0",
  )
  return fig


def competitor_radar(df: pd.DataFrame) -> go.Figure:
  if df.empty:
    df = pd.DataFrame({
        "Competitor": ["A", "B", "C"],
        "Brand Strength": [70, 85, 60],
        "Innovation Score": [75, 65, 80],
    })
  categories = [c for c in df.columns if c != "Competitor"]
  fig = go.Figure()
  for _, row in df.iterrows():
    fig.add_trace(go.Scatterpolar(
        r=[row[c] for c in categories],
        theta=categories,
        fill="toself",
        name=row["Competitor"],
    ))
  fig.update_layout(
      polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
      title="Competitor Comparison",
      paper_bgcolor="rgba(0,0,0,0)",
      font_color="#e2e8f0",
  )
  return fig


def competitor_bar(df: pd.DataFrame) -> go.Figure:
  if df.empty:
    return competitor_radar(df)
  fig = px.bar(
      df,
      x="Competitor",
      y="Brand Strength",
      color="Competitor",
      title="Brand Strength by Competitor",
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color="#e2e8f0",
      showlegend=False,
  )
  return fig


def swot_matrix(swot: dict) -> None:
  """Render SWOT as 2x2 layout."""
  cols = st.columns(2)
  with cols[0]:
    st.markdown("#### Strengths")
    for s in swot.get("strengths", [])[:6]:
      st.markdown(f"- {s}")
    st.markdown("#### Weaknesses")
    for w in swot.get("weaknesses", [])[:6]:
      st.markdown(f"- {w}")
  with cols[1]:
    st.markdown("#### Opportunities")
    for o in swot.get("opportunities", [])[:6]:
      st.markdown(f"- {o}")
    st.markdown("#### Threats")
    for t in swot.get("threats", [])[:6]:
      st.markdown(f"- {t}")


def trend_line() -> go.Figure:
  """Sample trend momentum chart."""
  df = pd.DataFrame({
      "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      "Trend Index": [62, 68, 71, 75, 78, 82],
      "Market Interest": [55, 58, 64, 70, 74, 79],
  })
  fig = px.line(
      df,
      x="Month",
      y=["Trend Index", "Market Interest"],
      title="Trend Momentum Forecast",
      markers=True,
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color="#e2e8f0",
      legend=dict(font_color="#e2e8f0"),
  )
  return fig


def render_analytics_charts(context: Optional[dict[str, Any]] = None) -> None:
  context = context or {}
  sentiment = context.get("sentiment", {})
  summary = sentiment.get("summary", {})
  reviews = sentiment.get("reviews", [])

  c1, c2 = st.columns(2)
  with c1:
    st.plotly_chart(sentiment_pie(summary), use_container_width=True)
  with c2:
    st.plotly_chart(sentiment_bar(reviews), use_container_width=True)

  from tools.analytics import competitor_comparison_table
  inp = context.get("input", {})
  comp_df = competitor_comparison_table(
      inp.get("competitors", ["Competitor A", "Competitor B"]),
      context.get("competitor_analysis", ""),
  )
  c3, c4 = st.columns(2)
  with c3:
    st.plotly_chart(competitor_bar(comp_df), use_container_width=True)
  with c4:
    st.plotly_chart(trend_line(), use_container_width=True)

  swot = context.get("swot", {})
  if swot:
    st.subheader("SWOT Matrix")
    swot_matrix(swot)
