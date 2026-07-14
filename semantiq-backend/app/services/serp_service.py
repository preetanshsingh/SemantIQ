"""
SerpAPI integration service.

Fetches Google SERP results for a keyword and extracts:
  1. Organic results (top 10 URLs + titles + snippets)
  2. People Also Ask questions (returned directly by SerpAPI)

Why SerpAPI over scraping Google directly?
  Google actively blocks scrapers. SerpAPI handles proxies, CAPTCHAs,
  and geolocation automatically. The free tier gives 100 searches/month
  which is enough to build and demo SemantIQ.

API docs: https://serpapi.com/search-api
"""

import os
from typing import List, Dict
import httpx
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
SERPAPI_BASE = "https://serpapi.com/search"

# Country code → Google domain mapping for localized results
COUNTRY_DOMAINS = {
    "US": "google.com",
    "UK": "google.co.uk",
    "IN": "google.co.in",
    "AU": "google.com.au",
    "CA": "google.ca",
    "DE": "google.de",
}

# Domains to skip during scraping — login walls, PDFs, etc.
SKIP_DOMAINS = {
    "youtube.com", "facebook.com", "twitter.com", "instagram.com",
    "linkedin.com", "reddit.com", "pinterest.com", "tiktok.com",
    "amazon.com", "ebay.com", "wikipedia.org",
}


def _is_scrapable(url: str) -> bool:
    """Filter out URLs we can't meaningfully scrape for content."""
    url_lower = url.lower()
    if url_lower.endswith(".pdf"):
        return False
    return not any(domain in url_lower for domain in SKIP_DOMAINS)


def fetch_serp(keyword: str, country: str = "US", num_results: int = 10) -> Dict:
    """
    Calls SerpAPI and returns structured SERP data.

    Returns:
        {
            "organic":  List[{"url": str, "title": str, "snippet": str}],
            "paa":      List[str],   # People Also Ask questions
            "keyword":  str,
        }

    Raises:
        ValueError: if SERPAPI_KEY is not set
        httpx.HTTPError: on network failure
    """
    if not SERPAPI_KEY:
        raise ValueError(
            "SERPAPI_KEY environment variable is not set. "
            "Get a free key at https://serpapi.com and add it to your .env file."
        )

    google_domain = COUNTRY_DOMAINS.get(country.upper(), "google.com")

    params = {
        "q": keyword,
        "google_domain": google_domain,
        "gl": country.lower(),
        "hl": "en",
        "num": num_results,
        "api_key": SERPAPI_KEY,
    }

    response = httpx.get(SERPAPI_BASE, params=params, timeout=15.0)
    response.raise_for_status()
    data = response.json()

    # Extract organic results
    organic = []
    for result in data.get("organic_results", []):
        url = result.get("link", "")
        if url and _is_scrapable(url):
            organic.append({
                "url": url,
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
            })

    # Extract PAA questions — SerpAPI returns these directly
    paa_questions = []
    for item in data.get("related_questions", []):
        question = item.get("question", "").strip()
        if question:
            paa_questions.append(question)

    return {
        "organic": organic[:num_results],
        "paa": paa_questions,
        "keyword": keyword,
    }
