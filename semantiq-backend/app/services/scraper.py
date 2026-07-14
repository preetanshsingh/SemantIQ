"""
Competitor page scraping service.

Takes a list of URLs from SerpAPI organic results and extracts clean
body text for the NLP engine to work on.

Design decisions:
  - Parallel scraping with httpx (concurrent requests, much faster than sequential)
  - BeautifulSoup for HTML parsing and text extraction
  - Aggressive noise removal: strips nav, footer, sidebar, scripts, ads
  - Conservative timeout (8s per page) to keep /analyze responsive
  - Graceful failure: a page that errors just gets skipped, not raising 500

What we extract per page:
  - All <h1>, <h2>, <h3> headings (important for content brief)
  - All <p> paragraph text (important for TF-IDF and SBERT)
  - Meta description as fallback if body is thin

Text length limits:
  - Min 200 chars: skip thin pages (boilerplate, 404s)
  - Max 8,000 chars per page: we don't need the whole page, just enough
    for the NLP models to work on. Keeps memory/compute reasonable.
"""

import asyncio
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup, Comment

# Tags that are content-free noise
_NOISE_TAGS = [
    "script", "style", "noscript", "nav", "footer", "header",
    "aside", "form", "iframe", "svg", "button", "input", "select",
    "textarea", "advertisement", "ads",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _extract_text(html: str, url: str = "") -> Optional[str]:
    """
    Parse HTML and return clean body text.
    Returns None if the page is too thin to be useful.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return None

    # Remove noise tags
    for tag in soup(["script", "style", "noscript", "nav", "footer",
                     "header", "aside", "form", "iframe", "svg"]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Extract headings first (higher signal density)
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) > 5:
            headings.append(text)

    # Extract paragraphs
    paragraphs = []
    for tag in soup.find_all("p"):
        text = tag.get_text(separator=" ", strip=True)
        if len(text) > 40:  # skip tiny/boilerplate paragraphs
            paragraphs.append(text)

    # Fallback: all body text if paragraphs are sparse
    if len(paragraphs) < 3:
        body = soup.find("body")
        if body:
            raw = body.get_text(separator=" ", strip=True)
            paragraphs = [raw]

    combined = " ".join(headings) + " " + " ".join(paragraphs)
    combined = " ".join(combined.split())  # normalize whitespace

    if len(combined) < 200:
        return None  # too thin — skip this page

    # Cap at 8,000 chars — enough for NLP, avoids memory bloat
    return combined[:8000]


async def _fetch_one(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Fetch a single URL and return extracted text, or None on failure."""
    try:
        response = await client.get(url, timeout=8.0, follow_redirects=True)
        if response.status_code != 200:
            return None
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return None
        return _extract_text(response.text, url)
    except Exception as e:
        print(f"[scraper] Skipping {url}: {e}")
        return None


async def _scrape_all(urls: List[str]) -> List[str]:
    """Scrape all URLs concurrently and return list of extracted texts."""
    async with httpx.AsyncClient(headers=_HEADERS) as client:
        tasks = [_fetch_one(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def scrape_competitor_pages(
    serp_results: List[Dict],
    max_pages: int = 5,
) -> List[str]:
    """
    Main entry point. Takes organic SERP results (from serp_service.fetch_serp)
    and returns a list of clean text strings, one per successfully scraped page.

    Args:
        serp_results: List of {"url": str, "title": str, "snippet": str}
        max_pages: Scrape at most this many pages (default 5, top 5 are sufficient
                   for the NLP models and keeps latency reasonable).

    Returns:
        List of clean text strings. Empty list if all pages fail.
    """
    urls = [r["url"] for r in serp_results[:max_pages]]
    if not urls:
        return []

    # Run the async scraping in a new event loop if called from sync context
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're inside an async context (FastAPI) — create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _scrape_all(urls))
                return future.result()
        else:
            return loop.run_until_complete(_scrape_all(urls))
    except RuntimeError:
        return asyncio.run(_scrape_all(urls))
