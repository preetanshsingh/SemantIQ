"""
POST /api/url-analyze

The "paste a URL" feature. Full pipeline:
  1. Scrape the user's URL → extract content + infer keyword
  2. Run SerpAPI for that keyword → get real competitors
  3. Scrape top 5 competitor pages
  4. Score user's page vs competitor corpus
  5. Score each competitor vs corpus
  6. Rank everyone, identify where the user sits
  7. Compute content gaps (missing words, entities, PAA)
  8. Return everything in one response
"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models import (
    URLAnalyzeRequest, URLAnalyzeResponse,
    CompetitorResult, ContentGap,
    ScoreBreakdownItem, WordRecommendation,
)
from app.services.url_service import scrape_url, infer_keyword
from app.services.serp_service import fetch_serp
from app.services.scraper import scrape_competitor_pages
from app.services.relevance import score_content
from app.services.information_gain import compute_information_gain
import app.cache as cache

router = APIRouter()


def _score_page(content: str, corpus: List[str], keyword: str) -> dict:
    """Score a single page against the competitor corpus."""
    if not content or not content.strip():
        return {"overall_score": 0, "breakdown": []}
    return score_content(content, corpus, keyword=keyword)


@router.post("/url-analyze", response_model=URLAnalyzeResponse)
def url_analyze(payload: URLAnalyzeRequest) -> URLAnalyzeResponse:
    """
    Full competitive analysis for a given URL.
    Returns the page's score, rank vs competitors, and what to fix.
    """

    # ── Step 1: Scrape the user's URL ──────────────────────────────────────
    try:
        page_data = scrape_url(payload.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    user_content = page_data["content"]
    if not user_content:
        raise HTTPException(
            status_code=422,
            detail="Could not extract content from this URL. The page may require login or be JavaScript-rendered."
        )

    # ── Step 2: Infer keyword ───────────────────────────────────────────────
    keyword = infer_keyword(page_data)

    # ── Step 3: SerpAPI → get real competitors ──────────────────────────────
    try:
        serp_data = fetch_serp(keyword=keyword, country=payload.country or "US")
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SerpAPI error: {e}")

    organic = serp_data["organic"]
    paa_questions = serp_data["paa"]

    # ── Step 4: Scrape competitor pages ─────────────────────────────────────
    competitor_texts = scrape_competitor_pages(organic, max_pages=3)

    if not competitor_texts:
        raise HTTPException(
            status_code=502,
            detail="Could not scrape enough competitor content. Try again in a moment."
        )

    # Store in cache so other endpoints can use this data too
    cache.store(
        keyword=keyword,
        competitor_texts=competitor_texts,
        paa_questions=paa_questions,
        serp_urls=[r["url"] for r in organic],
    )

    # ── Step 5: Score the user's page vs competitor corpus ──────────────────
    user_score_data = _score_page(user_content, competitor_texts, keyword)
    user_score = user_score_data["overall_score"]
    user_breakdown = user_score_data.get("breakdown", [])

    # ── Step 6: Score each competitor vs corpus ──────────────────────────────
    competitor_results: List[CompetitorResult] = []
    for i, (comp_text, serp_result) in enumerate(zip(competitor_texts, organic[:len(competitor_texts)])):
        # Score competitor against the rest of the corpus (excluding itself)
        other_texts = [t for j, t in enumerate(competitor_texts) if j != i]
        if not other_texts:
            other_texts = competitor_texts
        comp_score_data = _score_page(comp_text, other_texts, keyword)
        competitor_results.append(CompetitorResult(
            rank=i + 1,
            url=serp_result["url"],
            title=serp_result.get("title", f"Result #{i+1}"),
            score=comp_score_data["overall_score"],
            is_you=False,
        ))

    # ── Step 7: Determine user's rank ────────────────────────────────────────
    # Insert user into the sorted list by score to estimate rank
    all_scores = [(r.score, r.url) for r in competitor_results]
    all_scores.append((user_score, payload.url))
    all_scores.sort(key=lambda x: -x[0])
    your_rank = next(
        (i + 1 for i, (s, u) in enumerate(all_scores) if u == payload.url),
        len(all_scores)
    )

    # ── Step 8: Compute content gaps ─────────────────────────────────────────
    # Missing words (top IG recommendations)
    missing_words = compute_information_gain(
        competitor_texts=competitor_texts,
        user_content=user_content,
        top_n=10,
    )

    content_gaps: List[ContentGap] = []

    # High-impact missing words
    for rec in missing_words[:5]:
        impact = "high" if rec["ig"] >= 70 else "medium" if rec["ig"] >= 50 else "low"
        content_gaps.append(ContentGap(
            type="word",
            value=rec["word"],
            impact=impact,
        ))

    # Uncovered PAA questions
    for q in paa_questions[:3]:
        content_gaps.append(ContentGap(
            type="paa",
            value=q,
            impact="high",
        ))

    return URLAnalyzeResponse(
        url=payload.url,
        inferred_keyword=keyword,
        your_score=user_score,
        your_rank=your_rank,
        total_competitors=len(competitor_results),
        breakdown=[ScoreBreakdownItem(**b) for b in user_breakdown],
        competitors=competitor_results,
        content_gaps=content_gaps,
        top_missing_words=[WordRecommendation(**w) for w in missing_words[:7]],
    )
