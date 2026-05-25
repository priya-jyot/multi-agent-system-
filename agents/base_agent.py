"""Base class for all MarketMind AI agents."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from tools.file_handler import save_agent_observation
from tools.groq_client import GroqClient, GroqNotAvailableError
from utils.logger import log_agent, log_error


class BaseAgent(ABC):
  """Lightweight agent inspired by CrewAI/LangChain patterns."""

  name: str = "base"
  display_name: str = "Base Agent"
  description: str = ""

  def __init__(self, llm: Optional[GroqClient] = None):
    self.llm = llm or GroqClient()
    self.last_output: str = ""
    self.status: str = "idle"
    self.duration_ms: int = 0

  @abstractmethod
  def run(self, context: dict[str, Any]) -> dict[str, Any]:
    """Execute agent task and return updated context slice."""

  def _generate(
      self,
      prompt: str,
      system: Optional[str] = None,
      fallback: str = "",
  ) -> str:
    try:
      return self.llm.generate(
          prompt,
          system=system or f"You are the {self.display_name}. Be concise and professional.",
          temperature=0.7,
      )
    except GroqNotAvailableError as e:
      log_error(self.name, str(e))
      return fallback or (
          f"[Offline mode] {self.display_name} could not reach Groq. "
          "Set GROQ_API_KEY in your .env file (see README)."
      )

  def execute(
      self,
      context: dict[str, Any],
      on_progress: Optional[Callable[[str], None]] = None,
  ) -> dict[str, Any]:
    """Run with logging and timing."""
    self.status = "running"
    log_agent(self.name, "started")
    if on_progress:
      on_progress(f"{self.display_name} started...")

    start = time.time()
    try:
      result = self.run(context)
      self.status = "completed"
      self.last_output = str(result.get("output", result.get(self.name, "")))[:5000]
      save_agent_observation(
          self.name,
          self.last_output[:1500],
          context.get("research_id", ""),
      )
      log_agent(self.name, "completed", "OK")
      if on_progress:
        on_progress(f"{self.display_name} completed.")
      return result
    except Exception as e:
      self.status = "error"
      log_error(self.name, str(e))
      log_agent(self.name, str(e), "ERROR")
      if on_progress:
        on_progress(f"{self.display_name} error: {e}")
      return {"error": str(e), "output": ""}
    finally:
      self.duration_ms = int((time.time() - start) * 1000)
