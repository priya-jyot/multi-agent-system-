"""Centralized logging for agents and workflows."""

from __future__ import annotations

import logging
from datetime import datetime

from config import AGENT_LOG, ERROR_LOG, EXECUTION_LOG, LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _file_handler(path, level=logging.INFO):
  h = logging.FileHandler(path, encoding="utf-8")
  h.setLevel(level)
  h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
  return h


def get_logger(name: str) -> logging.Logger:
  logger = logging.getLogger(name)
  if logger.handlers:
    return logger
  logger.setLevel(logging.INFO)
  logger.addHandler(_file_handler(EXECUTION_LOG))
  return logger


def log_agent(agent: str, message: str, status: str = "INFO") -> None:
  line = f"{datetime.now().isoformat()} | {agent} | {status} | {message}\n"
  try:
    with open(AGENT_LOG, "a", encoding="utf-8") as f:
      f.write(line)
  except OSError:
    pass


def log_error(source: str, message: str) -> None:
  line = f"{datetime.now().isoformat()} | {source} | {message}\n"
  try:
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
      f.write(line)
  except OSError:
    pass
  logging.getLogger(source).error(message)


def log_workflow(step: str, detail: str = "") -> None:
  get_logger("workflow").info("%s — %s", step, detail or "ok")
