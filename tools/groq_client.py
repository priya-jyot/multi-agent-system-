"""Groq cloud LLM client with retries and error handling."""

from __future__ import annotations

import logging
import os
import re
from typing import Generator, Optional

from config import (
    ERROR_LOG,
    GROQ_API_KEY,
    GROQ_AVAILABLE_MODELS,
    GROQ_MAX_RETRIES,
    GROQ_MODEL,
    GROQ_TIMEOUT,
)

logger = logging.getLogger(__name__)


class GroqNotAvailableError(Exception):
    """Raised when Groq API is not configured or unreachable."""


class GroqClient:
    """LLM client for Groq's OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = GROQ_MODEL,
        timeout: int = GROQ_TIMEOUT,
        max_retries: int = GROQ_MAX_RETRIES,
    ):
        self.api_key = (api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")).strip()
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = None

    def _get_client(self):
        if not self.api_key:
            raise GroqNotAvailableError(
                "Groq API key not set. Add GROQ_API_KEY to a .env file or environment variables."
            )
        if self._client is None:
            try:
                from groq import Groq
            except ImportError as e:
                raise GroqNotAvailableError(
                    "groq package not installed. Run: pip install groq"
                ) from e
            self._client = Groq(api_key=self.api_key, timeout=self.timeout)
        return self._client

    def is_available(self) -> bool:
        """True if a Groq API key is configured (no network call)."""
        return bool(self.api_key and len(self.api_key) > 10)

    def test_connection(self) -> tuple[bool, str]:
        """Verify API key with a minimal completion. Use sparingly."""
        if not self.is_available():
            return False, "API key not set"
        try:
            client = self._get_client()
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0,
            )
            return True, "Connected"
        except Exception as e:
            return False, str(e)

    def list_models(self) -> list[str]:
        """Return supported Groq models for the UI."""
        return list(GROQ_AVAILABLE_MODELS)

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        """Generate text from a prompt. Returns full string (streaming not used by agents)."""
        if stream:
            return self._stream_generate(prompt, system, temperature)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, temperature=temperature)

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str:
        """Chat completion via Groq API."""
        client = self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                )
                return (response.choices[0].message.content or "").strip()
            except Exception as e:
                last_error = e
                logger.warning("Groq attempt %s failed: %s", attempt, e)
                _log_error(f"Groq retry {attempt}: {e}")

        raise GroqNotAvailableError(
            f"Failed after {self.max_retries} attempts: {last_error}"
        )

    def _stream_generate(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
    ) -> Generator[str, None, None]:
        client = self._get_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


# Prompt templates for agents
PROMPTS = {
    "market_research": """You are a senior market research analyst.
Analyze the following business context and provide structured insights.

Business: {business_name}
Industry: {industry}
Target Audience: {target_audience}
Competitors: {competitors}

Provide:
1. Industry overview
2. Target audience analysis
3. Market opportunities
4. Market gaps
5. Key findings summary

Be specific, professional, and actionable. Use bullet points where helpful.""",

    "competitor": """You are a competitive intelligence specialist.
Based on market context and any scraped data, analyze competitors.

Business: {business_name}
Industry: {industry}
Competitors: {competitors}
Market context: {market_context}
Web snippets: {web_data}

Provide:
1. Competitor overview
2. Product/feature comparison
3. Pricing analysis (estimates if exact data unavailable)
4. Strengths and weaknesses per competitor
5. Competitor battle card summary""",

    "sentiment": """You are a customer insights analyst.
Analyze sentiment from reviews and feedback.

Business: {business_name}
Review data: {review_data}
Sentiment scores: {sentiment_scores}

Provide:
1. Overall sentiment summary
2. Positive themes
3. Negative themes / pain points
4. Recommendations to improve customer satisfaction""",

    "trend": """You are a trend forecasting analyst.
Identify emerging trends and future market direction.

Business: {business_name}
Industry: {industry}
Market research: {market_context}
News/trend data: {trend_data}

Provide:
1. Emerging trends (3-5)
2. Trend patterns
3. Future opportunities
4. Market direction forecast (6-12 months)""",

    "strategy": """You are a chief marketing officer advisor.
Create a marketing strategy based on all prior research.

Business: {business_name}
Industry: {industry}
Target Audience: {target_audience}
Full context: {full_context}

Provide:
1. Positioning statement
2. Branding recommendations
3. Campaign ideas (3-5)
4. Channel strategy (social, email, content, etc.)
5. Customer targeting tactics
6. 90-day marketing plan outline""",

    "swot": """Create a SWOT analysis for this business.

Business: {business_name}
Industry: {industry}
Context: {full_context}

Format as:
Strengths: (bullet list)
Weaknesses: (bullet list)
Opportunities: (bullet list)
Threats: (bullet list)""",

    "report_executive": """Write a concise executive summary (200-300 words) for this marketing intelligence report.

Business: {business_name}
Key findings: {full_context}""",
}


def format_prompt(template_key: str, **kwargs) -> str:
    """Fill a prompt template with kwargs."""
    template = PROMPTS.get(template_key, "")
    return template.format(**{k: kwargs.get(k, "N/A") for k in _extract_placeholders(template)})


def _extract_placeholders(template: str) -> list[str]:
    return list(set(re.findall(r"\{(\w+)\}", template)))


def _log_error(msg: str) -> None:
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except OSError:
        pass
