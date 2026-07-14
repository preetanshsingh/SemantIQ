"""
Response/request schemas for SemantIQ's API.

IMPORTANT: every field name here matches a key already used in the React
frontend's src/data/mockData.js. Keep it that way — when these stub
endpoints are replaced with real NLP logic, the frontend should not need
to change at all, only the data source (fetch() instead of a local import).
"""

from typing import List, Optional
from pydantic import BaseModel


# ---------- Shared request body ----------

class AnalyzeRequest(BaseModel):
    keyword: str
    country: Optional[str] = "US"


class ScoreRequest(BaseModel):
    content: str
    keyword: str


# ---------- /analyze ----------

class AnalyzeResponse(BaseModel):
    keyword: str
    country: str
    status: str  # "queued" | "complete" — stubbed as instant "complete" for now
    serp_results_found: int


# ---------- /score ----------

class ScoreBreakdownItem(BaseModel):
    label: str
    score: int


class ScoreResponse(BaseModel):
    overall_score: int
    breakdown: List[ScoreBreakdownItem]


# ---------- /recommendations (word + Information Gain) ----------

class WordRecommendation(BaseModel):
    word: str
    ig: int          # Information Gain, 0-100 — the signature SemantIQ signal
    category: str     # "Core" | "Semantic" | "Entity"
    points: int


# ---------- /paa ----------

class PAAItem(BaseModel):
    question: str
    answered: bool
    points: Optional[int] = None


# ---------- /entities ----------

class EntityItem(BaseModel):
    entity: str
    type: str
    inKG: bool
    count: int


# ---------- /readability ----------

class ReadabilityMetric(BaseModel):
    label: str
    value: str
    grade: str
    good: bool


# ---------- /brief ----------

class ContentBrief(BaseModel):
    h1: str
    h2s: List[str]


# ---------- /links ----------

class LinkSuggestion(BaseModel):
    anchor_text: str
    target_url: str
    relevance: int   # 0-100
    type: str        # "internal" | "external"


# ---------- /url-analyze ----------

class URLAnalyzeRequest(BaseModel):
    url: str
    country: Optional[str] = "US"


class CompetitorResult(BaseModel):
    rank: int
    url: str
    title: str
    score: int
    is_you: bool


class ContentGap(BaseModel):
    type: str    # "word" | "entity" | "paa"
    value: str
    impact: str  # "high" | "medium" | "low"


class URLAnalyzeResponse(BaseModel):
    url: str
    inferred_keyword: str
    your_score: int
    your_rank: int
    total_competitors: int
    breakdown: List[ScoreBreakdownItem]
    competitors: List[CompetitorResult]
    content_gaps: List[ContentGap]
    top_missing_words: List[WordRecommendation]
