"""
Named Entity Recognition + Knowledge Graph linking service.

Uses spaCy for entity extraction (en_core_web_sm) and a KG lookup
stub (real Google Knowledge Graph Search API call goes in step 4/step 3 TODO).

Graceful fallback: if the spaCy model hasn't been downloaded yet, falls back
to a simple regex-based NER approach. The API keeps working; quality is lower.

Phase 1 connection:
  NER identifies the "Entity Richness" of content — a key quality signal.
  KG linking tells us which entities are authoritative (in Google's KG)
  vs just mentioned casually. Google's ranking systems strongly weight
  content that correctly uses KG-linked entities.
"""

from __future__ import annotations
import re
from typing import List, Dict, Optional
from collections import Counter

# Lazy-load spaCy (requires en_core_web_sm to be downloaded)
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError) as e:
            print(f"[entities] spaCy model unavailable: {e}. Using regex fallback.")
            _nlp = False
    return _nlp if _nlp else None


# -----------------------------------------------------------------------
# Regex fallback NER — crude but keeps the endpoint live without spaCy
# -----------------------------------------------------------------------

FALLBACK_TYPE_PATTERNS = {
    "Disease": re.compile(
        r'\b(diabetes|cancer|hypertension|obesity|alzheimer|parkinson|asthma'
        r'|arthritis|depression|anxiety|disease|disorder|syndrome)\b', re.I
    ),
    "Drug": re.compile(
        r'\b(metformin|insulin|aspirin|ibuprofen|paracetamol|medication'
        r'|drug|tablet|capsule|dose|dosage)\b', re.I
    ),
    "Protein": re.compile(
        r'\b(insulin|hemoglobin|albumin|collagen|keratin|enzyme|hormone'
        r'|receptor|antibody|protein)\b', re.I
    ),
    "Biomarker": re.compile(
        r'\b(hba1c|glucose|cholesterol|triglyceride|creatinine|bmi'
        r'|blood pressure|blood sugar)\b', re.I
    ),
    "Organ": re.compile(
        r'\b(pancreas|liver|kidney|heart|lung|brain|stomach|intestine'
        r'|thyroid|spleen)\b', re.I
    ),
}

# Entities we know are in the Google Knowledge Graph (sampled whitelist).
# TODO (step 4): replace with real Google Knowledge Graph Search API calls.
KNOWN_KG_ENTITIES = {
    "insulin", "pancreas", "blood sugar", "glucose", "metformin",
    "hemoglobin", "hba1c", "diabetes", "hypertension", "cholesterol",
    "kidney", "liver", "heart", "brain", "thyroid",
}


def _regex_ner(text: str) -> List[Dict]:
    """Fallback NER using compiled regex patterns."""
    found: Dict[str, str] = {}
    for entity_type, pattern in FALLBACK_TYPE_PATTERNS.items():
        for match in pattern.finditer(text):
            term = match.group(0).lower()
            if term not in found:
                found[term] = entity_type

    # Count occurrences in original text
    text_lower = text.lower()
    results = []
    for term, etype in found.items():
        count = len(re.findall(re.escape(term), text_lower))
        results.append({
            "entity": term,
            "type": etype,
            "inKG": term in KNOWN_KG_ENTITIES,
            "count": count,
        })
    return sorted(results, key=lambda x: -x["count"])


def _spacy_ner(text: str, nlp) -> List[Dict]:
    """Full spaCy NER pipeline."""
    doc = nlp(text)
    entity_counts: Counter = Counter()
    entity_labels: Dict[str, str] = {}

    for ent in doc.ents:
        key = ent.text.lower().strip()
        entity_counts[key] += 1
        # Map spaCy NER labels to our friendlier type names
        label_map = {
            "PERSON": "Person", "ORG": "Organization", "GPE": "Location",
            "DISEASE": "Disease", "CHEMICAL": "Drug", "PRODUCT": "Product",
            "NORP": "Group", "EVENT": "Event", "WORK_OF_ART": "Creative",
        }
        entity_labels[key] = label_map.get(ent.label_, ent.label_)

    results = []
    for entity, count in entity_counts.most_common(15):
        results.append({
            "entity": entity,
            "type": entity_labels.get(entity, "Entity"),
            "inKG": entity in KNOWN_KG_ENTITIES,
            "count": count,
        })
    return results


def extract_entities(content: str) -> List[dict]:
    """
    Main entry point for the /entities endpoint.
    Uses spaCy if available, otherwise falls back to regex NER.
    """
    if not content or not content.strip():
        return []

    nlp = _get_nlp()
    if nlp:
        return _spacy_ner(content, nlp)
    else:
        return _regex_ner(content)


def entity_coverage_score(
    user_entities: List[dict],
    competitor_texts: List[str],
) -> int:
    """
    Computes a 0-100 entity coverage score:
    how many entities prominent in the SERP corpus appear in the user's content.

    Called by the /score endpoint to contribute to the overall score.
    """
    if not competitor_texts:
        return 0

    # Extract entities from competitor texts using the same pipeline
    all_competitor_text = " ".join(competitor_texts)
    competitor_entities = {e["entity"] for e in extract_entities(all_competitor_text)}
    user_entity_set = {e["entity"] for e in user_entities}

    if not competitor_entities:
        return 0

    overlap = len(competitor_entities & user_entity_set)
    return min(100, int((overlap / len(competitor_entities)) * 100))
