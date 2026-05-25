"""Lightweight public web scraping with graceful failure handling."""

from __future__ import annotations

import logging
import re
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 12


def _safe_get(url: str) -> Optional[str]:
  try:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text
  except requests.RequestException as e:
    logger.warning("Scrape failed for %s: %s", url, e)
    return None


def extract_text(html: str, max_chars: int = 4000) -> str:
  soup = BeautifulSoup(html, "html.parser")
  for tag in soup(["script", "style", "nav", "footer", "header"]):
    tag.decompose()
  text = " ".join(soup.stripped_strings)
  text = re.sub(r"\s+", " ", text)
  return text[:max_chars]


def scrape_url(url: str) -> dict:
  """Scrape a single public URL."""
  html = _safe_get(url)
  if not html:
    return {"url": url, "success": False, "text": "", "error": "Could not fetch URL"}
  return {"url": url, "success": True, "text": extract_text(html), "error": None}


def scrape_competitor_pages(competitors: list[str]) -> list[dict]:
  """Attempt to scrape competitor homepages (https)."""
  results = []
  for name in competitors[:5]:
    name = name.strip()
    if not name:
      continue
    # Try common URL patterns
    slug = re.sub(r"[^a-z0-9]", "", name.lower())
    urls = [
        f"https://www.{slug}.com",
        f"https://{slug}.com",
    ]
    found = False
    for url in urls:
      data = scrape_url(url)
      if data.get("success") and len(data.get("text", "")) > 200:
        data["competitor"] = name
        results.append(data)
        found = True
        break
    if not found:
      results.append({
          "competitor": name,
          "url": "",
          "success": False,
          "text": f"No public page scraped for {name}. Use LLM knowledge.",
          "error": "scrape_failed",
      })
  return results


def fetch_news_snippets(query: str, max_items: int = 5) -> list[dict]:
  """
  Fetch news-style snippets via DuckDuckGo HTML (no API key).
  Falls back to empty list on failure.
  """
  items = []
  url = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' news market trends')}"
  html = _safe_get(url)
  if not html:
    return items
  soup = BeautifulSoup(html, "html.parser")
  for result in soup.select(".result")[:max_items]:
    title_el = result.select_one(".result__a")
    snippet_el = result.select_one(".result__snippet")
    if title_el:
      items.append({
          "title": title_el.get_text(strip=True),
          "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
          "link": title_el.get("href", ""),
      })
  return items


def aggregate_web_context(
    industry: str,
    competitors: list[str],
    business_name: str,
) -> dict:
  """Collect web data for agents."""
  news = fetch_news_snippets(f"{industry} {business_name}")
  competitor_data = scrape_competitor_pages(competitors)
  news_text = "\n".join(
      f"- {n.get('title', '')}: {n.get('snippet', '')}" for n in news
  )
  comp_text = "\n".join(
      f"[{c.get('competitor', 'Unknown')}]: {c.get('text', '')[:800]}"
      for c in competitor_data
  )
  return {
      "news": news,
      "competitor_scrapes": competitor_data,
      "news_summary": news_text or "No news snippets retrieved (offline or blocked).",
      "competitor_summary": comp_text or "No competitor pages scraped.",
  }
