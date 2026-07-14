from fastapi import APIRouter, Query
from typing import List
from app.models import WordRecommendation
from app.services.information_gain import compute_information_gain
import app.cache as cache

router = APIRouter()

_SAMPLE_TEXTS = [
    "Insulin resistance is a key factor in type 2 diabetes. Blood glucose levels must be carefully monitored. HbA1c test provides a 3-month average. Glycemic index helps understand how foods affect blood sugar.",
    "Pancreatic beta cells are destroyed in type 1 diabetes. Fasting blood sugar tests are used for diagnosis. Endocrinologist specializes in hormonal disorders including diabetes.",
    "Managing diabetes requires monitoring blood glucose. Glycemic index helps diabetics choose foods. Exercise improves insulin sensitivity.",
]


@router.get("/recommendations", response_model=List[WordRecommendation])
def get_recommendations(
    keyword: str = Query(...),
    content: str = Query(""),
) -> List[WordRecommendation]:
    """
    Real IG-ranked word recommendations.
    Uses real competitor texts from cache if /analyze was called first.
    """
    cached = cache.get(keyword)
    competitor_texts = cached["competitor_texts"] if cached and cached["competitor_texts"] else _SAMPLE_TEXTS

    results = compute_information_gain(
        competitor_texts=competitor_texts,
        user_content=content,
        top_n=15,
    )
    return [WordRecommendation(**item) for item in results]
