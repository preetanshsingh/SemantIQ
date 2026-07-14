"""
In-memory keyword cache.

Stores the results of a /analyze call (competitor texts, PAA questions,
SERP metadata) so all other endpoints can use real data without re-fetching
on every request.

Structure per keyword:
  {
    "competitor_texts": List[str],   # scraped text from top-N SERP pages
    "paa_questions":    List[str],   # People Also Ask from SerpAPI response
    "serp_urls":        List[str],   # URLs of the competitor pages scraped
    "cached_at":        float,       # unix timestamp of when data was cached
  }

Cache invalidation: 6 hours (SERP results don't change meaningfully faster).

TODO (Milestone 4 — persistence layer):
  Replace this with a SQLite/PostgreSQL store so:
  - Cache survives server restarts
  - Multiple users don't share/overwrite each other's data
  - Historical score tracking works across sessions
"""

import time
from typing import Optional

_CACHE: dict = {}
_TTL_SECONDS = 6 * 60 * 60  # 6 hours


def store(keyword: str, competitor_texts: list, paa_questions: list, serp_urls: list) -> None:
    """Store SERP + scraping results for a keyword."""
    _CACHE[keyword.lower().strip()] = {
        "competitor_texts": competitor_texts,
        "paa_questions": paa_questions,
        "serp_urls": serp_urls,
        "cached_at": time.time(),
    }


def get(keyword: str) -> Optional[dict]:
    """
    Retrieve cached data for a keyword. Returns None if:
    - keyword was never analyzed
    - cache entry is older than TTL
    """
    key = keyword.lower().strip()
    entry = _CACHE.get(key)
    if entry is None:
        return None
    if time.time() - entry["cached_at"] > _TTL_SECONDS:
        del _CACHE[key]
        return None
    return entry


def has(keyword: str) -> bool:
    return get(keyword) is not None


def clear(keyword: str) -> None:
    _CACHE.pop(keyword.lower().strip(), None)
