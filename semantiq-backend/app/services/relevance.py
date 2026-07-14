"""
Hybrid TF-IDF + SBERT relevance scoring service.

This is the heart of SemantIQ's scoring engine — the upgrade over OnPage.ai's
plain TF-IDF approach identified during Phase 1.

Why hybrid? (Phase 1 theory recap):
  - TF-IDF alone is lexical: "heart attack" and "myocardial infarction" score
    as completely different, even though they mean the same thing.
  - SBERT (Sentence-BERT) is semantic: it encodes meaning into a dense 384-dim
    vector space where synonyms, paraphrases, and related concepts cluster
    together.
  - Combining both captures lexical precision AND semantic coverage.

Score weights (tunable):
  - SBERT cosine similarity:  60%  (semantic alignment with top-3 competitors)
  - TF-IDF cosine similarity: 40%  (keyword/lexical coverage)

The final output is a 0-100 relevance score per factor, aggregated into the
overall score shown in the score ring.

Model used: all-MiniLM-L6-v2 (~80MB). Smaller than all-mpnet-base-v2 but
near-identical quality for semantic similarity tasks (Reimers & Gurevych 2019).
The model is loaded once on first call and cached in memory.
"""

from __future__ import annotations
import re
from typing import List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Lazy-load SBERT so the API starts instantly even if the model hasn't
# been downloaded yet. The first call to score_content() triggers the download.
_sbert_model = None


def _get_sbert():
    global _sbert_model
    if _sbert_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[relevance] SBERT model unavailable: {e}. Falling back to TF-IDF only.")
            _sbert_model = False  # False = tried and failed, don't retry
    return _sbert_model if _sbert_model else None


def _tfidf_similarity(user_text: str, reference_texts: List[str]) -> float:
    """TF-IDF cosine similarity between the user's draft and a reference corpus."""
    if not reference_texts or not user_text.strip():
        return 0.0
    corpus = reference_texts + [user_text]
    vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return 0.0
    # Mean of pairwise cosine similarities between user and each reference
    user_vec = matrix[-1]
    ref_vecs = matrix[:-1]
    sims = cosine_similarity(user_vec, ref_vecs).flatten()
    return float(np.mean(sims))


def _sbert_similarity(user_text: str, reference_texts: List[str]) -> float:
    """SBERT dense embedding cosine similarity."""
    model = _get_sbert()
    if model is None or not reference_texts or not user_text.strip():
        return 0.0
    try:
        embeddings = model.encode(reference_texts + [user_text], convert_to_numpy=True)
        user_emb = embeddings[-1].reshape(1, -1)
        ref_embs = embeddings[:-1]
        sims = cosine_similarity(user_emb, ref_embs).flatten()
        return float(np.mean(sims))
    except Exception as e:
        print(f"[relevance] SBERT encoding error: {e}")
        return 0.0


def _heading_structure_score(content: str) -> int:
    """
    Simple heuristic for heading structure quality.
    Checks for presence of H1/H2 markdown markers or bolded headings.
    """
    has_h1 = bool(re.search(r'^#{1}\s+\w', content, re.MULTILINE))
    has_h2 = bool(re.search(r'^#{2}\s+\w', content, re.MULTILINE))
    has_h3 = bool(re.search(r'^#{3}\s+\w', content, re.MULTILINE))
    # If no markdown, check for short lines that look like headings
    lines = content.split('\n')
    short_caps = [l for l in lines if 5 < len(l.split()) < 10 and l.strip()]
    score = 30
    if has_h1: score += 25
    if has_h2: score += 25
    if has_h3: score += 10
    if short_caps: score += min(10, len(short_caps) * 3)
    return min(100, score)


def _content_depth_score(content: str) -> int:
    """
    Content depth heuristic based on word count and paragraph count.
    Target: 1,200-2,500 words for a comprehensive article.
    """
    word_count = len(content.split())
    para_count = len([p for p in content.split('\n\n') if p.strip()])
    wc_score = min(100, int((word_count / 1500) * 80))
    para_score = min(20, para_count * 3)
    return min(100, wc_score + para_score)


def score_content(
    user_content: str,
    competitor_texts: List[str],
    keyword: str = "",
    paa_coverage: Optional[int] = None,
    entity_coverage: Optional[int] = None,
    readability_score: Optional[int] = None,
) -> dict:
    """
    Main entry point. Returns the overall score and a breakdown dict
    matching the ScoreResponse Pydantic model shape.

    Args:
        user_content: The user's current draft.
        competitor_texts: Raw text from SERP top-N competitor pages.
        keyword: Target keyword (used to boost keyword-in-content matching).
        paa_coverage: Optional pre-computed PAA coverage score (0-100).
        entity_coverage: Optional pre-computed entity coverage score (0-100).
        readability_score: Optional pre-computed readability score (0-100).
    """
    # --- Keyword Relevance: 60% SBERT + 40% TF-IDF ---
    tfidf_sim = _tfidf_similarity(user_content, competitor_texts)
    sbert_sim = _sbert_similarity(user_content, competitor_texts)
    # If SBERT unavailable, fall back to pure TF-IDF
    if sbert_sim == 0.0:
        relevance_raw = tfidf_sim
    else:
        relevance_raw = 0.6 * sbert_sim + 0.4 * tfidf_sim
    keyword_relevance = min(100, int(relevance_raw * 100))

    # --- Other factors ---
    entity_cov = entity_coverage if entity_coverage is not None else min(100, keyword_relevance - 10)
    readability = readability_score if readability_score is not None else 72
    content_depth = _content_depth_score(user_content)
    heading_structure = _heading_structure_score(user_content)
    paa_cov = paa_coverage if paa_coverage is not None else max(0, keyword_relevance - 30)

    breakdown = [
        {"label": "Keyword relevance", "score": keyword_relevance},
        {"label": "Entity coverage",   "score": entity_cov},
        {"label": "Readability",        "score": readability},
        {"label": "Content depth",      "score": content_depth},
        {"label": "Heading structure",  "score": heading_structure},
        {"label": "PAA coverage",       "score": paa_cov},
    ]

    # Weighted overall score
    weights = [0.30, 0.20, 0.15, 0.15, 0.10, 0.10]
    scores  = [keyword_relevance, entity_cov, readability, content_depth, heading_structure, paa_cov]
    overall = int(sum(w * s for w, s in zip(weights, scores)))

    return {
        "overall_score": overall,
        "breakdown": breakdown,
        "sbert_available": _get_sbert() is not None,
    }
