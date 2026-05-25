"""High-level research pipeline API for UI."""

from __future__ import annotations

from typing import Any, Callable, Optional

import pandas as pd

from tools.file_handler import save_uploaded_file
from tools.groq_client import GroqClient, GroqNotAvailableError
from tools.web_scraper import aggregate_web_context
from workflows.orchestration import AgentOrchestrator


def validate_input(data: dict) -> tuple[bool, str]:
  if not data.get("business_name", "").strip():
    return False, "Business/product name is required."
  if not data.get("industry", "").strip():
    return False, "Industry is required."
  return True, ""


def parse_competitors(text: str) -> list[str]:
  if not text:
    return []
  parts = [p.strip() for p in text.replace(";", ",").split(",")]
  return [p for p in parts if p]


def build_input(
    business_name: str,
    industry: str,
    target_audience: str,
    competitors_text: str,
) -> dict:
  return {
      "business_name": business_name.strip(),
      "industry": industry.strip(),
      "target_audience": target_audience.strip() or "General consumers",
      "competitors": parse_competitors(competitors_text),
  }


def check_groq_status() -> dict:
  client = GroqClient()
  available = client.is_available()
  models = client.list_models() if available else []
  return {
      "available": available,
      "models": models,
      "configured_model": client.model,
  }


def run_research(
    input_data: dict,
    uploaded_reviews=None,
    model: Optional[str] = None,
    on_step: Optional[Callable] = None,
    on_log: Optional[Callable] = None,
) -> tuple[dict[str, Any], Optional[str]]:
  """
  Run full research pipeline.
  Returns (context, error_message).
  """
  ok, msg = validate_input(input_data)
  if not ok:
    return {}, msg

  orchestrator = AgentOrchestrator(model=model)
  ctx = orchestrator.context

  # Pre-fetch web data
  try:
    web = aggregate_web_context(
        input_data["industry"],
        input_data.get("competitors", []),
        input_data["business_name"],
    )
    orchestrator.context["web_data"] = web
  except Exception:
    orchestrator.context["web_data"] = {
        "news_summary": "Web collection skipped.",
        "competitor_summary": "",
    }

  if uploaded_reviews is not None:
    path = save_uploaded_file(uploaded_reviews)
    if path and path.suffix.lower() == ".csv":
      try:
        orchestrator.context["reviews_df"] = pd.read_csv(path)
      except Exception:
        pass

  try:
    result = orchestrator.run_full_pipeline(
        input_data,
        on_step=on_step,
        on_log=on_log,
    )
    return result, None
  except GroqNotAvailableError as e:
    # Still try pipeline — agents have fallbacks
    result = orchestrator.run_full_pipeline(
        input_data,
        on_step=on_step,
        on_log=on_log,
    )
    return result, str(e)
  except Exception as e:
    return orchestrator.context, str(e)


def run_strategy_pipeline(
    input_data: dict,
    model: Optional[str] = None,
) -> tuple[dict, Optional[str]]:
  ok, msg = validate_input(input_data)
  if not ok:
    return {}, msg
  orch = AgentOrchestrator(model=model)
  try:
    return orch.run_strategy_only(input_data), None
  except Exception as e:
    return orch.context, str(e)
