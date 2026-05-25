"""Local file I/O: JSON, CSV, reports, uploads."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from config import (
    AGENT_MEMORY_FILE,
    CHAT_HISTORY_FILE,
    DATA_DIR,
    MEMORY_DIR,
    REPORTS_DIR,
    RESEARCH_HISTORY_FILE,
    UPLOADS_DIR,
)


def _read_json(path: Path, default: Any = None) -> Any:
  if not path.exists():
    return default if default is not None else []
  try:
    with open(path, "r", encoding="utf-8") as f:
      return json.load(f)
  except (json.JSONDecodeError, OSError):
    return default if default is not None else []


def _write_json(path: Path, data: Any) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


def load_research_history() -> list[dict]:
  return _read_json(RESEARCH_HISTORY_FILE, [])


def save_research_entry(entry: dict) -> None:
  history = load_research_history()
  entry.setdefault("id", datetime.now().strftime("%Y%m%d_%H%M%S"))
  entry.setdefault("timestamp", datetime.now().isoformat())
  history.insert(0, entry)
  _write_json(RESEARCH_HISTORY_FILE, history[:100])


def load_agent_memory() -> list[dict]:
  return _read_json(AGENT_MEMORY_FILE, [])


def save_agent_observation(agent: str, observation: str, research_id: str = "") -> None:
  memory = load_agent_memory()
  memory.insert(0, {
      "agent": agent,
      "observation": observation[:2000],
      "research_id": research_id,
      "timestamp": datetime.now().isoformat(),
  })
  _write_json(AGENT_MEMORY_FILE, memory[:200])


def load_chat_history() -> list[dict]:
  return _read_json(CHAT_HISTORY_FILE, [])


def append_chat(role: str, content: str) -> None:
  chats = load_chat_history()
  chats.append({
      "role": role,
      "content": content,
      "timestamp": datetime.now().isoformat(),
  })
  _write_json(CHAT_HISTORY_FILE, chats[-500:])


def save_report_text(report_id: str, content: str) -> Path:
  path = REPORTS_DIR / f"{report_id}.txt"
  path.write_text(content, encoding="utf-8")
  return path


def save_report_json(report_id: str, data: dict) -> Path:
  path = REPORTS_DIR / f"{report_id}.json"
  _write_json(path, data)
  return path


def load_report(report_id: str) -> Optional[dict]:
  path = REPORTS_DIR / f"{report_id}.json"
  if path.exists():
    return _read_json(path, {})
  return None


def list_reports() -> list[dict]:
  reports = []
  for p in sorted(REPORTS_DIR.glob("*.json"), reverse=True):
    data = _read_json(p, {})
    reports.append({
        "id": p.stem,
        "business_name": data.get("input", {}).get("business_name", p.stem),
        "timestamp": data.get("timestamp", ""),
        "path": str(p),
    })
  return reports


def save_uploaded_file(uploaded_file) -> Optional[Path]:
  """Save Streamlit uploaded file to uploads/."""
  if uploaded_file is None:
    return None
  dest = UPLOADS_DIR / uploaded_file.name
  with open(dest, "wb") as f:
    f.write(uploaded_file.getbuffer())
  return dest


def load_sample_csv(name: str = "sample_reviews.csv") -> pd.DataFrame:
  path = DATA_DIR / name
  if path.exists():
    return pd.read_csv(path)
  return pd.DataFrame()


def export_dataframe_csv(df: pd.DataFrame, filename: str) -> Path:
  path = DATA_DIR / filename
  df.to_csv(path, index=False)
  return path
