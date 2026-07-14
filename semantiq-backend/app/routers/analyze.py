"""
/analyze endpoint — the orchestrator of the full SemantIQ pipeline.

Flow:
  1. Call SerpAPI → get organic top-10 URLs + PAA questions
  2. Scrape competitor pages in parallel → get clean text
  3. Store everything in the keyword cache
  4. Other endpoints (/score, /recommendations, /paa, /brief) pull from
     that cache and return real NLP results instead of mock data

This is the endpoint that makes everything else real.
"""

from fastapi import APIRouter, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.serp_service import fetch_serp
from app.services.scraper import scrape_competitor_pages
import app.cache as cache

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    Full pipeline: SerpAPI → scrape → cache.
    After this call succeeds, /score, /recommendations, /paa, and /brief
    all serve real data for this keyword automatically.
    """
    try:
        # Step 1: fetch SERP results + PAA from SerpAPI
        serp_data = fetch_serp(
            keyword=payload.keyword,
            country=payload.country or "US",
            num_results=10,
        )
    except ValueError as e:
        # SERPAPI_KEY not configured
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SerpAPI error: {e}")

    organic_results = serp_data["organic"]
    paa_questions = serp_data["paa"]

    # Step 2: scrape competitor pages in parallel (top 5 for speed)
    competitor_texts = scrape_competitor_pages(organic_results, max_pages=5)

    # Step 3: store everything in cache — all other endpoints use this
    serp_urls = [r["url"] for r in organic_results]
    cache.store(
        keyword=payload.keyword,
        competitor_texts=competitor_texts,
        paa_questions=paa_questions,
        serp_urls=serp_urls,
    )

    return AnalyzeResponse(
        keyword=payload.keyword,
        country=payload.country or "US",
        status="complete",
        serp_results_found=len(organic_results),
    )
