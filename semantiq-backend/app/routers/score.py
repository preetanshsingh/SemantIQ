from fastapi import APIRouter
from app.models import ScoreRequest, ScoreResponse, ScoreBreakdownItem
from app.services.relevance import score_content
import app.cache as cache

router = APIRouter()

_SAMPLE_TEXTS = [
    "Insulin resistance is a key factor in type 2 diabetes. Blood glucose levels must be carefully monitored. HbA1c test provides a 3-month average. Glycemic index helps understand how foods affect blood sugar.",
    "Pancreatic beta cells are destroyed in type 1 diabetes. Fasting blood sugar tests are used for diagnosis. Endocrinologist specializes in hormonal disorders including diabetes.",
    "Managing diabetes requires monitoring blood glucose. Glycemic index helps diabetics choose foods. Exercise improves insulin sensitivity and reduces insulin resistance significantly.",
]


@router.post("/score", response_model=ScoreResponse)
def score_content_endpoint(payload: ScoreRequest) -> ScoreResponse:
    """
    Real SBERT + TF-IDF relevance scoring.
    Uses real scraped competitor texts if /analyze has been called for
    this keyword, otherwise falls back to sample texts.
    """
    cached = cache.get(payload.keyword)
    competitor_texts = cached["competitor_texts"] if cached and cached["competitor_texts"] else _SAMPLE_TEXTS

    result = score_content(
        user_content=payload.content,
        competitor_texts=competitor_texts,
        keyword=payload.keyword,
    )
    return ScoreResponse(
        overall_score=result["overall_score"],
        breakdown=[ScoreBreakdownItem(**item) for item in result["breakdown"]],
    )
