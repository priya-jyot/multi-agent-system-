"""Multi-agent orchestration — CrewAI/LangChain-inspired lightweight coordinator."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Optional

from agents import (
    CompetitorAgent,
    MarketResearchAgent,
    ReportAgent,
    SentimentAgent,
    StrategyAgent,
    TrendAgent,
)
from tools.file_handler import save_research_entry
from tools.groq_client import GroqClient
from utils.logger import log_workflow


class AgentOrchestrator:
  """
  Coordinates specialized agents in sequence.
  Each agent receives shared context and adds its outputs.
  """

  PIPELINE = [
      ("market_research", MarketResearchAgent),
      ("competitor", CompetitorAgent),
      ("sentiment", SentimentAgent),
      ("trend", TrendAgent),
      ("strategy", StrategyAgent),
      ("report", ReportAgent),
  ]

  def __init__(self, model: Optional[str] = None):
    self.llm = GroqClient(model=model) if model else GroqClient()
    self.agents = {}
    for key, cls in self.PIPELINE:
      self.agents[key] = cls(llm=self.llm)
    self.context: dict[str, Any] = {}
    self.timeline: list[dict] = []

  def reset(self, input_data: dict) -> None:
    self.context = {
        "input": input_data,
        "research_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "agent_timeline": [],
        "started_at": datetime.now().isoformat(),
    }
    self.timeline = []

  def run_full_pipeline(
      self,
      input_data: dict,
      on_step: Optional[Callable[[str, str, int, int], None]] = None,
      on_log: Optional[Callable[[str], None]] = None,
  ) -> dict[str, Any]:
    """Execute all agents in order."""
    self.reset(input_data)
    total = len(self.PIPELINE)

    for idx, (key, _) in enumerate(self.PIPELINE):
      agent = self.agents[key]
      step_name = agent.display_name
      log_workflow(step_name, "start")

      if on_step:
        on_step(key, step_name, idx + 1, total)

      def progress(msg: str):
        if on_log:
          on_log(msg)

      result = agent.execute(self.context, on_progress=progress)
      self.context.update(result)
      self.timeline.append({
          "agent": key,
          "display_name": step_name,
          "status": agent.status,
          "duration_ms": agent.duration_ms,
          "timestamp": datetime.now().isoformat(),
      })
      self.context["agent_timeline"] = self.timeline
      log_workflow(step_name, agent.status)

    save_research_entry({
        "id": self.context["research_id"],
        "input": input_data,
        "timeline": self.timeline,
        "report_id": self.context.get("report_id"),
    })
    return self.context

  def run_single_agent(
      self,
      agent_key: str,
      input_data: Optional[dict] = None,
  ) -> dict[str, Any]:
    """Run one agent against current or new context."""
    if input_data:
      self.reset(input_data)
    if agent_key not in self.agents:
      raise ValueError(f"Unknown agent: {agent_key}")
    agent = self.agents[agent_key]
    result = agent.execute(self.context)
    self.context.update(result)
    return self.context

  def run_strategy_only(self, input_data: dict) -> dict[str, Any]:
    """Quick path: market + strategy + report."""
    self.reset(input_data)
    for key in ("market_research", "strategy", "report"):
      agent = self.agents[key]
      result = agent.execute(self.context)
      self.context.update(result)
    return self.context

  def get_agent_status(self) -> list[dict]:
    return [
        {
            "key": key,
            "name": self.agents[key].display_name,
            "status": self.agents[key].status,
            "duration_ms": self.agents[key].duration_ms,
        }
        for key, _ in self.PIPELINE
    ]
