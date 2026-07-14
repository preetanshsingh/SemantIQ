from fastapi import APIRouter, Query
from typing import List
from app.models import PAAItem
from app.mock_data import PAA_ITEMS
import app.cache as cache

router = APIRouter()


@router.get("/paa", response_model=List[PAAItem])
def get_paa(keyword: str = Query(...)) -> List[PAAItem]:
    """
    Returns PAA questions. Uses real SerpAPI PAA data if /analyze has
    been called for this keyword, otherwise returns mock data.
    """
    cached = cache.get(keyword)

    if cached and cached["paa_questions"]:
        # Real PAA from SerpAPI — all marked as unanswered by default.
        # TODO: use SBERT to detect which questions are answered in the
        # user's content and set answered=True accordingly.
        return [
            PAAItem(question=q, answered=False, points=5)
            for q in cached["paa_questions"]
        ]

    # Fallback to mock data
    return [PAAItem(**item) for item in PAA_ITEMS]
