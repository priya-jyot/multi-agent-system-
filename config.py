"""Central configuration for MarketMind AI."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# Data directories
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = ROOT / "logs"
UPLOADS_DIR = ROOT / "uploads"
MEMORY_DIR = ROOT / "memory"

# Ensure directories exist
for _dir in (DATA_DIR, REPORTS_DIR, LOGS_DIR, UPLOADS_DIR, MEMORY_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Groq API settings (https://console.groq.com)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT = 120
GROQ_MAX_RETRIES = 3
GROQ_AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

# Memory files
RESEARCH_HISTORY_FILE = MEMORY_DIR / "research_history.json"
AGENT_MEMORY_FILE = MEMORY_DIR / "agent_observations.json"
CHAT_HISTORY_FILE = MEMORY_DIR / "chat_history.json"

# Log files
EXECUTION_LOG = LOGS_DIR / "execution_logs.txt"
ERROR_LOG = LOGS_DIR / "errors.txt"
AGENT_LOG = LOGS_DIR / "agent_logs.txt"

# UI
APP_TITLE = "MarketMind AI"
APP_TAGLINE = "Multi-Agent Marketing Research & Competitive Intelligence"

# Agent display names
AGENT_NAMES = {
    "market_research": "Market Research Agent",
    "competitor": "Competitor Intelligence Agent",
    "sentiment": "Sentiment Analysis Agent",
    "trend": "Trend Forecasting Agent",
    "strategy": "Marketing Strategy Agent",
    "report": "Report Generation Agent",
}
