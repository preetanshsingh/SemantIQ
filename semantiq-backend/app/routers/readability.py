from fastapi import APIRouter, Body
from typing import List
from app.models import ReadabilityMetric
from app.services.readability_service import analyze_readability

router = APIRouter()


@router.post("/readability", response_model=List[ReadabilityMetric])
def get_readability(content: str = Body(..., embed=True)) -> List[ReadabilityMetric]:
    """
    Computes real readability and AI-detection metrics for submitted content.
    Uses textstat (Flesch, FK Grade) + the Phase 1 perplexity/burstiness
    AI-detection model.
    """
    results = analyze_readability(content)
    return [ReadabilityMetric(**item) for item in results]
