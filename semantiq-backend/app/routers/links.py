from fastapi import APIRouter, Body
from typing import List
from app.models import LinkSuggestion
from app.mock_data import LINK_SUGGESTIONS

router = APIRouter()


@router.post("/links", response_model=List[LinkSuggestion])
def get_link_suggestions(content: str = Body(..., embed=True)) -> List[LinkSuggestion]:
    """
    Suggests internal/external links relevant to the submitted content.
    Currently stubbed with fixed mock data regardless of submitted content.

    TODO (Milestone 3): replace with the real link relevancy scorer —
    likely cosine similarity between content embeddings and a sitemap
    index, or a GNN over the site's internal link graph as hypothesized
    in the OnPage.ai reverse-engineering analysis.
    """
    return [LinkSuggestion(**item) for item in LINK_SUGGESTIONS]
