"""
URL analysis service.

Given a URL, this service:
  1. Scrapes the page and extracts clean text
  2. Infers the target keyword from title / H1 / meta description
  3. Returns structured page data for the URL analysis pipeline

This is the entry point for the "paste a URL" feature — the user doesn't
need to know their keyword, we figure it out from their page automatically.
"""

import re
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape_url(url: str) -> dict:
    """
    Fetches and parses a URL. Returns:
    {
        "title":       str,
        "h1":          str,
        "meta_desc":   str,
        "headings":    List[str],
        "content":     str,   # clean body text
    }
    Raises httpx.HTTPError or ValueError on failure.
    """
    try:
        response = httpx.get(url, headers=_HEADERS, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Could not fetch URL (HTTP {e.response.status_code})")
    except Exception as e:
        raise ValueError(f"Could not reach URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        # Remove site name suffix (e.g. " | Healthline")
        title = re.split(r'\s*[\|\-–—]\s*', title)[0].strip()

    # H1
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else ""

    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta.get("content", "").strip() if meta else ""

    # All headings
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) > 4:
            headings.append(text)

    # Body paragraphs
    paragraphs = []
    for tag in soup.find_all("p"):
        text = tag.get_text(separator=" ", strip=True)
        if len(text) > 40:
            paragraphs.append(text)

    content = " ".join(headings) + " " + " ".join(paragraphs)
    content = " ".join(content.split())[:8000]

    return {
        "title": title,
        "h1": h1,
        "meta_desc": meta_desc,
        "headings": headings,
        "content": content,
    }


def infer_keyword(page_data: dict) -> str:
    """
    Infers the primary target keyword from a scraped page.

    Priority order:
    1. H1 (most semantically intentional)
    2. Title tag (usually keyword-optimized)
    3. TF-IDF top bigram/trigram from body content (fallback)
    """
    # Clean helper
    def clean(text: str) -> str:
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return " ".join(text.split())

    # 1. H1 is the strongest signal
    if page_data.get("h1") and len(page_data["h1"].split()) >= 2:
        h1 = clean(page_data["h1"])
        # Take first 4 words — avoids overly long H1s
        return " ".join(h1.split()[:4])

    # 2. Title tag
    if page_data.get("title") and len(page_data["title"].split()) >= 2:
        title = clean(page_data["title"])
        return " ".join(title.split()[:4])

    # 3. TF-IDF fallback on body content
    content = page_data.get("content", "")
    if content:
        try:
            vec = TfidfVectorizer(ngram_range=(2, 3), stop_words="english", max_features=20)
            matrix = vec.fit_transform([content])
            scores = np.asarray(matrix.todense()).flatten()
            top_idx = scores.argmax()
            return vec.get_feature_names_out()[top_idx]
        except Exception:
            pass

    return "content optimization"
