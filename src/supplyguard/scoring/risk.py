"""Deterministic risk scoring."""

from __future__ import annotations

from supplyguard.config import ScannerConfig


def compute_risk(findings: list[dict[str, object]], metadata: dict[str, object] | None = None, name_similarity: dict[str, object] | None = None, config: ScannerConfig | None = None) -> tuple[int, str]:
    config = config or ScannerConfig()
    total = 0
    for item in findings:
        score = item.get("score_contribution") or 0
        if isinstance(score, int):
            total += score
    if metadata and metadata.get("available") == "AVAILABLE" and metadata.get("author") is None:
        total += 5
    if name_similarity and name_similarity.get("match"):
        total += 15
    if total >= config.score_block_threshold:
        decision = "BLOCK"
    elif total >= config.score_warning_threshold:
        decision = "WARN"
    else:
        decision = "ALLOW"
    return total, decision
