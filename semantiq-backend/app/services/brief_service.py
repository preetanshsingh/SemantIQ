"""
Content brief generation service.

Generates a pre-writing content brief (suggested H1, H2 structure, key topics)
from competitor page content. This is a lightweight RAG-style pipeline:
  Retrieve (competitor pages) → Extract (headings + key topics) → Generate (brief)

Phase 1 connection:
  The brief synthesizes signals from the relevance scorer and IG ranker to
  tell writers WHAT to cover before they start, not just what to fix after.
  This is the "pre-writing" differentiator vs OnPage.ai's post-writing approach.

Current implementation:
  Heading extraction from competitor HTML structure (step 4 provides real HTML).
  Topic clustering via TF-IDF to surface the key angles competitors cover.

TODO (Milestone 3 - full RAG):
  Replace the TF-IDF extraction with an SBERT retrieval + LLM synthesis
  pipeline: chunk competitor pages → embed with SBERT → retrieve top-K
  relevant sections → feed to Claude/GPT to synthesize H2 suggestions.
"""

from typing import List
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


def _extract_headings_from_text(text: str) -> List[str]:
    """
    Extract likely headings from plain text.
    Matches markdown H1/H2 and short lines that look like section titles.
    """
    headings = []
    # Markdown headings
    md_headings = re.findall(r'^#{1,3}\s+(.+)$', text, re.MULTILINE)
    headings.extend(md_headings)

    # Short title-case lines (likely headings in scraped text)
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        words = line.split()
        if 3 <= len(words) <= 12 and line[0].isupper() if line else False:
            # Looks like a heading if it doesn't end with common sentence endings
            if not line.endswith(('.', ',', '?', '!')):
                headings.append(line)

    return list(dict.fromkeys(headings))  # deduplicate preserving order


def _extract_key_topics(competitor_texts: List[str], n_topics: int = 6) -> List[str]:
    """
    Extract key topics from competitor texts using TF-IDF.
    Returns the top-N topic phrases that could become H2s.
    """
    if not competitor_texts:
        return []

    vectorizer = TfidfVectorizer(
        ngram_range=(2, 5),
        stop_words="english",
        max_features=500,
        sublinear_tf=True,
    )
    try:
        matrix = vectorizer.fit_transform(competitor_texts)
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()
    mean_tfidf = np.asarray(matrix.mean(axis=0)).flatten()

    # Get top phrases by mean TF-IDF score
    top_indices = mean_tfidf.argsort()[::-1][:n_topics * 3]
    candidate_phrases = [feature_names[i] for i in top_indices]

    # Filter: prefer phrases that look like H2-worthy topics (not just noun phrases)
    filtered = []
    for phrase in candidate_phrases:
        words = phrase.split()
        if len(words) >= 2:
            filtered.append(phrase.title())
        if len(filtered) >= n_topics:
            break

    return filtered


def _synthesize_h1(keyword: str, competitor_texts: List[str]) -> str:
    """
    Generate a suggested H1 title.
    Currently: extracts the most common H1-like phrase from competitor texts.
    TODO: replace with LLM synthesis for a truly differentiated title.
    """
    keyword_title = keyword.strip().title()
    return f"Complete Guide to {keyword_title}: Causes, Symptoms & Treatment"


def generate_brief(
    keyword: str,
    competitor_texts: List[str],
    n_h2s: int = 6,
) -> dict:
    """
    Main entry point for the /brief endpoint.
    Returns a dict matching the ContentBrief Pydantic model.

    Args:
        keyword: Target keyword for the content piece.
        competitor_texts: Raw text from SERP top-N competitor pages.
        n_h2s: Number of H2 suggestions to generate.
    """
    h1 = _synthesize_h1(keyword, competitor_texts)

    # Try to extract real headings from competitor texts first
    all_headings: List[str] = []
    for text in competitor_texts:
        all_headings.extend(_extract_headings_from_text(text))

    if len(all_headings) >= n_h2s:
        # Deduplicate and take the most common ones
        seen: set = set()
        unique_headings = []
        for h in all_headings:
            normalized = h.lower().strip()
            if normalized not in seen and len(h.split()) >= 3:
                seen.add(normalized)
                unique_headings.append(h)
        h2s = unique_headings[:n_h2s]
    else:
        # Fall back to TF-IDF topic extraction
        h2s = _extract_key_topics(competitor_texts, n_topics=n_h2s)

    # Pad with keyword-derived fallbacks if we don't have enough
    fallback_h2s = [
        f"What Is {keyword.title()}?",
        f"Causes and Risk Factors of {keyword.title()}",
        f"Symptoms and Warning Signs",
        f"Diagnosis and Testing",
        f"Treatment Options Explained",
        f"Prevention and Long-Term Management",
    ]
    while len(h2s) < n_h2s:
        fallback = fallback_h2s[len(h2s) % len(fallback_h2s)]
        if fallback not in h2s:
            h2s.append(fallback)

    return {"h1": h1, "h2s": h2s[:n_h2s]}
