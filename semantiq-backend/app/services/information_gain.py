"""
Information Gain word recommendation service.

This is SemantIQ's signature differentiator — the IG bar that every word
recommendation card displays. No competitor tool exposes this signal.

Theory (from Phase 1):
  Information Gain measures how much a term reduces uncertainty about
  topic relevance. Given:
    - D_serp: document set = SERP top-N competitor pages
    - D_user: user's current draft

  For each candidate term t:
    IG(t) = H(D_serp) − H(D_serp | t)

  where H is the Shannon entropy of the topic-relevance distribution.

  In practice we approximate this with TF-IDF term weights:
  terms that appear frequently across SERP pages but are ABSENT from
  the user's draft have the highest potential Information Gain.

Pipeline:
  1. Fit a TF-IDF vectorizer on the SERP corpus (competitor pages)
  2. Extract top-N candidate terms by IDF weight (rare-in-corpus = low;
     frequent-in-corpus = high IDF score)
  3. Filter out terms already well-covered in the user's draft
  4. Score each remaining term by: corpus_tf × (1 - user_coverage)
  5. Normalize to 0-100 range, assign category label, return ranked list
"""

import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


# Candidate term categories, matched by simple heuristic on corpus co-occurrence.
# TODO: replace with spaCy NER labels once the model is available.
CATEGORY_KEYWORDS = {
    "Entity": ["disease", "syndrome", "disorder", "drug", "protein", "gene",
                "doctor", "hospital", "treatment", "therapy", "acid", "vitamin"],
    "Core": ["type", "cause", "symptom", "sign", "risk", "level", "blood",
             "sugar", "glucose", "insulin", "cell", "body"],
}


def _classify_term(term: str, corpus_texts: List[str]) -> str:
    """Assign a rough category to a term based on co-occurrence heuristics."""
    term_lower = term.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in term_lower for kw in keywords):
            return category
    return "Semantic"


def _user_coverage(term: str, user_text: str) -> float:
    """
    Returns 0.0–1.0: how well the user's draft already covers this term.
    Simple word overlap for now.
    TODO: replace with SBERT cosine similarity once relevance.py is integrated.
    """
    user_lower = user_text.lower()
    words = term.lower().split()
    covered = sum(1 for w in words if w in user_lower)
    return covered / len(words) if words else 0.0


def _estimate_points(ig_score: float) -> int:
    """Map an IG score to a UI point award (1–6)."""
    if ig_score >= 85: return 6
    if ig_score >= 75: return 5
    if ig_score >= 65: return 4
    if ig_score >= 50: return 3
    if ig_score >= 35: return 2
    return 1


def compute_information_gain(
    competitor_texts: List[str],
    user_content: str,
    top_n: int = 20,
    min_df: int = 2,
) -> List[dict]:
    """
    Core IG pipeline. Returns a list of word recommendation dicts
    matching the WordRecommendation Pydantic model shape.

    Args:
        competitor_texts: Raw text content scraped from SERP top-N pages.
        user_content: The user's current draft text.
        top_n: How many recommendations to return.
        min_df: Minimum document frequency — terms must appear in at least
                this many competitor docs to be considered.
    """
    if not competitor_texts:
        return []

    # 1. Fit TF-IDF on the SERP corpus
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),   # unigrams, bigrams, trigrams
        min_df=min_df,
        max_df=0.95,          # ignore terms in >95% of docs (stop-word-like)
        stop_words="english",
        sublinear_tf=True,    # log(1+tf) smoothing
        max_features=2000,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(competitor_texts)
    except ValueError:
        # Not enough documents or vocabulary
        return []

    feature_names = vectorizer.get_feature_names_out()

    # 2. Mean TF-IDF weight per term across the corpus
    mean_tfidf = np.asarray(tfidf_matrix.mean(axis=0)).flatten()

    # 3. Score by corpus weight × (1 − user coverage)
    scored_terms = []
    for idx, term in enumerate(feature_names):
        corpus_weight = float(mean_tfidf[idx])
        if corpus_weight < 0.01:
            continue
        coverage = _user_coverage(term, user_content)
        # Terms already fully covered by the user contribute nothing
        if coverage >= 0.9:
            continue
        raw_score = corpus_weight * (1.0 - coverage)
        scored_terms.append((term, raw_score, coverage))

    if not scored_terms:
        return []

    # 4. Normalize to 0–100 IG scale
    max_score = max(s for _, s, _ in scored_terms)
    min_score = min(s for _, s, _ in scored_terms)
    score_range = max_score - min_score or 1.0

    results = []
    for term, raw_score, _ in sorted(scored_terms, key=lambda x: -x[1])[:top_n]:
        ig = round(((raw_score - min_score) / score_range) * 100)
        results.append({
            "word": term,
            "ig": ig,
            "category": _classify_term(term, competitor_texts),
            "points": _estimate_points(ig),
        })

    return results
