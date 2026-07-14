from fastapi import APIRouter, Body
from typing import List
from app.models import EntityItem
from app.services.entity_service import extract_entities

router = APIRouter()


@router.post("/entities", response_model=List[EntityItem])
def get_entities(content: str = Body(..., embed=True)) -> List[EntityItem]:
    """
    Real NER using spaCy (en_core_web_sm) with regex fallback if the model
    isn't downloaded. Each entity is checked against a KG whitelist — step 4
    replaces the whitelist with real Google Knowledge Graph API lookups.
    """
    results = extract_entities(content)
    return [EntityItem(**item) for item in results]
