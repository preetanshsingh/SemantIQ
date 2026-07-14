"""
Mock data mirroring src/data/mockData.js on the frontend.

When the real NLP engine (SBERT, spaCy, TF-IDF, textstat, FAISS) is wired
in, each router file imports from here today and will import from a real
`services/*.py` module instead — the route signatures and response shapes
should not need to change.
"""

WORD_RECOMMENDATIONS = [
    {"word": "insulin resistance", "ig": 89, "category": "Core", "points": 6},
    {"word": "blood glucose levels", "ig": 85, "category": "Core", "points": 5},
    {"word": "HbA1c test", "ig": 78, "category": "Semantic", "points": 5},
    {"word": "glycemic index", "ig": 72, "category": "Semantic", "points": 4},
    {"word": "pancreatic beta cells", "ig": 68, "category": "Entity", "points": 4},
    {"word": "fasting blood sugar", "ig": 65, "category": "Semantic", "points": 4},
    {"word": "endocrinologist", "ig": 61, "category": "Entity", "points": 3},
]

PAA_ITEMS = [
    {"question": "What are the early signs of diabetes?", "answered": False, "points": 6},
    {"question": "How is type 2 different from type 1?", "answered": True, "points": None},
    {"question": "Can diabetes be reversed with diet?", "answered": False, "points": 6},
    {"question": "What is a normal blood sugar level?", "answered": True, "points": None},
    {"question": "What foods should diabetics avoid?", "answered": False, "points": 5},
]

ENTITIES = [
    {"entity": "insulin", "type": "Protein", "inKG": True, "count": 3},
    {"entity": "pancreas", "type": "Organ", "inKG": True, "count": 2},
    {"entity": "blood sugar", "type": "Biomarker", "inKG": True, "count": 5},
    {"entity": "metformin", "type": "Drug", "inKG": False, "count": 0},
    {"entity": "HbA1c", "type": "Biomarker", "inKG": False, "count": 0},
]

READABILITY_METRICS = [
    {"label": "Flesch Reading Ease", "value": "64.2", "grade": "Standard", "good": True},
    {"label": "FK Grade Level", "value": "8.4", "grade": "Grade 8", "good": True},
    {"label": "Passive Voice", "value": "14%", "grade": "Moderate", "good": False},
    {"label": "Avg Sentence Length", "value": "18 words", "grade": "Optimal", "good": True},
    {"label": "Burstiness Index", "value": "0.71", "grade": "Human-like", "good": True},
    {"label": "AI Probability", "value": "31%", "grade": "Likely human", "good": True},
]

CONTENT_BRIEF = {
    "h1": "Complete Guide to Diabetes Management: Symptoms, Treatment & Prevention",
    "h2s": [
        "What Is Diabetes? Types, Causes, Risk Factors",
        "Early Warning Signs You Should Not Ignore",
        "How Diabetes Is Diagnosed: Tests & Procedures",
        "Managing Blood Sugar: Diet, Exercise, Medication",
        "HbA1c and Key Biomarkers Explained",
        "Can Type 2 Diabetes Be Reversed?",
    ],
}

SCORE_BREAKDOWN = [
    {"label": "Keyword relevance", "score": 78},
    {"label": "Entity coverage", "score": 62},
    {"label": "Readability", "score": 84},
    {"label": "Content depth", "score": 70},
    {"label": "Heading structure", "score": 58},
    {"label": "PAA coverage", "score": 40},
]

LINK_SUGGESTIONS = [
    {"anchor_text": "blood glucose monitoring", "target_url": "/guides/glucose-monitoring", "relevance": 91, "type": "internal"},
    {"anchor_text": "type 2 diabetes diet plan", "target_url": "/guides/diabetes-diet", "relevance": 84, "type": "internal"},
    {"anchor_text": "American Diabetes Association", "target_url": "https://diabetes.org", "relevance": 76, "type": "external"},
    {"anchor_text": "insulin therapy basics", "target_url": "/guides/insulin-therapy", "relevance": 69, "type": "internal"},
]
