from fastapi import APIRouter, Query
from app.models import ContentBrief
from app.services.brief_service import generate_brief
from app.mock_data import CONTENT_BRIEF
import app.cache as cache

router = APIRouter()

_SAMPLE_TEXTS = [
    "What Is Diabetes? Types, Causes, Risk Factors. Diabetes is a metabolic condition. Early Warning Signs You Should Not Ignore. How Diabetes Is Diagnosed. Managing Blood Sugar Diet Exercise Medication. HbA1c and Key Biomarkers Explained.",
    "Understanding Insulin Resistance. Blood Glucose Monitoring Best Practices. Diabetes Complications. Medications for Type 2 Diabetes. Diet and Nutrition for Diabetics. Exercise and Physical Activity for Blood Sugar Control.",
    "Diagnosing Diabetes: Fasting Blood Sugar, HbA1c, and Oral Glucose Tests. Living With Type 1 vs Type 2 Diabetes. Preventing Diabetes Through Lifestyle Modifications. Advanced Treatment Options.",
]


@router.get("/brief", response_model=ContentBrief)
def get_brief(keyword: str = Query(...)) -> ContentBrief:
    """
    Generates a pre-writing content brief.
    Uses real scraped competitor headings if /analyze was called first.
    """
    cached = cache.get(keyword)
    competitor_texts = cached["competitor_texts"] if cached and cached["competitor_texts"] else _SAMPLE_TEXTS

    result = generate_brief(keyword=keyword, competitor_texts=competitor_texts)
    return ContentBrief(**result)
