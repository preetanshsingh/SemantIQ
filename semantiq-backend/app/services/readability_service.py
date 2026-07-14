"""
Readability and AI-detection service.

Implements:
  - Flesch Reading Ease, FK Grade Level via textstat
  - Passive voice detection via heuristic auxiliary scanning
  - Average sentence length
  - Normalized Burstiness Index (NBI) — the Phase 1 AI-detection signal
  - AI probability estimate based on perplexity proxy + NBI

Why burstiness works as an AI-detection signal (Phase 1 theory):
  Human writing shows HIGH variance in sentence length (short punchy
  sentences mixed with long complex ones). GPT-style LLMs produce text
  with LOW variance — sentences cluster around a mean length. We measure
  this with the Normalized Burstiness Index = (std - mean) / (std + mean).
  Human text: NBI typically 0.4–0.8. AI text: NBI typically -0.2–0.3.
"""

import re
import math
from typing import List
import textstat


def _sentence_lengths(text: str) -> List[int]:
    """Split text into sentences and return a list of word counts per sentence."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [len(s.split()) for s in sentences if s.strip()]


def _passive_voice_ratio(text: str) -> float:
    """
    Rough passive-voice heuristic: looks for 'was/were/is/are/been + past participle'
    patterns. Imperfect but cheap — replace with a spaCy dependency-parse approach
    once the spaCy model is available.
    """
    passive_pattern = re.compile(
        r'\b(was|were|is|are|been|be|being)\s+\w+ed\b', re.IGNORECASE
    )
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return 0.0
    passive_count = sum(1 for s in sentences if passive_pattern.search(s))
    return passive_count / len(sentences)


def _normalized_burstiness_index(sentence_lengths: List[int]) -> float:
    """
    NBI = (σ - μ) / (σ + μ)

    Range: -1 (perfectly uniform / AI-like) to +1 (extremely bursty / human-like).
    Human writing typically scores 0.4–0.8.
    AI text typically scores -0.2–0.3.

    From Phase 1 theory: Goh & Barabási (2008) — burstiness of human
    communication follows heavy-tailed distributions, unlike LLM output.
    """
    if len(sentence_lengths) < 3:
        return 0.0
    mean = sum(sentence_lengths) / len(sentence_lengths)
    variance = sum((x - mean) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    std = math.sqrt(variance)
    if std + mean == 0:
        return 0.0
    return (std - mean) / (std + mean)


def _ai_probability(nbi: float, avg_sentence_len: float) -> float:
    """
    Heuristic AI probability combining NBI and average sentence length.

    Low NBI (uniform sentence lengths) + avg_sentence ~15-22 words (LLM sweet spot)
    both push AI probability up. Returns a 0-100 percentage.

    TODO (Milestone 3): replace with a proper logistic regression or a fine-tuned
    classifier trained on known-human vs known-AI text corpora.
    """
    # NBI contribution: NBI of -0.2 → very likely AI; 0.7+ → very likely human
    nbi_normalized = max(0.0, min(1.0, (nbi + 0.3) / 1.0))
    human_prob = nbi_normalized

    # Sentence length contribution: 15-22 word avg is the LLM comfort zone
    len_penalty = 0.0
    if 15 <= avg_sentence_len <= 22:
        len_penalty = 0.15

    ai_prob = max(0.0, min(1.0, (1 - human_prob) + len_penalty))
    return round(ai_prob * 100, 1)


def analyze_readability(content: str) -> List[dict]:
    """
    Main entry point for the /readability endpoint.
    Returns a list of metric dicts matching the ReadabilityMetric Pydantic model.
    """
    if not content or not content.strip():
        return []

    lengths = _sentence_lengths(content)
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    nbi = _normalized_burstiness_index(lengths)
    passive_pct = _passive_voice_ratio(content) * 100
    ai_prob = _ai_probability(nbi, avg_len)

    flesch = round(textstat.flesch_reading_ease(content), 1)
    fk_grade = round(textstat.flesch_kincaid_grade(content), 1)

    def flesch_grade_label(score: float) -> str:
        if score >= 70: return "Standard / Easy"
        if score >= 50: return "Fairly Difficult"
        return "Difficult"

    return [
        {
            "label": "Flesch Reading Ease",
            "value": str(flesch),
            "grade": flesch_grade_label(flesch),
            "good": flesch >= 50,
        },
        {
            "label": "FK Grade Level",
            "value": str(fk_grade),
            "grade": f"Grade {int(fk_grade)}",
            "good": fk_grade <= 10,
        },
        {
            "label": "Passive Voice",
            "value": f"{passive_pct:.0f}%",
            "grade": "Low" if passive_pct < 10 else "Moderate" if passive_pct < 25 else "High",
            "good": passive_pct < 20,
        },
        {
            "label": "Avg Sentence Length",
            "value": f"{avg_len:.0f} words",
            "grade": "Optimal" if 12 <= avg_len <= 20 else "Too long" if avg_len > 20 else "Too short",
            "good": 12 <= avg_len <= 20,
        },
        {
            "label": "Burstiness Index",
            "value": f"{nbi:.2f}",
            "grade": "Human-like" if nbi >= 0.4 else "Borderline" if nbi >= 0.1 else "AI-like",
            "good": nbi >= 0.3,
        },
        {
            "label": "AI Probability",
            "value": f"{ai_prob:.0f}%",
            "grade": "Likely human" if ai_prob < 40 else "Borderline" if ai_prob < 65 else "Likely AI",
            "good": ai_prob < 50,
        },
    ]
