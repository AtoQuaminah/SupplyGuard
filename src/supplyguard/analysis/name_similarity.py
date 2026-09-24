"""Package name similarity analysis."""

from __future__ import annotations

import re
from difflib import SequenceMatcher


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    value = value.lower().strip()
    value = re.sub(r"[-_.]+", "-", value)
    return value


def analyze_name_similarity(candidate_name: str | None, reference_names: list[str] | None = None, threshold: float = 0.75) -> dict[str, object]:
    candidate = normalize_name(candidate_name)
    reference_names = reference_names or [
        "requests",
        "numpy",
        "pandas",
        "django",
        "setuptools",
        "pip",
        "urllib3",
    ]
    best_match = None
    best_score = 0.0
    for reference_name in reference_names:
        ref = normalize_name(reference_name)
        score = SequenceMatcher(None, candidate, ref).ratio()
        if score > best_score:
            best_score = score
            best_match = reference_name
    if best_match is None:
        return {
            "candidate_name": candidate,
            "reference_name": None,
            "similarity": 0.0,
            "method": "SequenceMatcher",
            "explanation": "No reference names were available for comparison.",
            "threshold": threshold,
            "match": False,
        }
    match = best_score >= threshold
    return {
        "candidate_name": candidate,
        "reference_name": best_match,
        "similarity": round(best_score, 4),
        "method": "SequenceMatcher",
        "explanation": f"The candidate name {candidate!r} is similar to {best_match!r} with score {best_score:.3f}.",
        "threshold": threshold,
        "match": match,
    }
