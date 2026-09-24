"""Data models for SupplyGuard."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    finding_id: str
    module: str
    rule_id: str
    category: str
    severity: str
    confidence: str
    score_contribution: int
    file_path: str | None = None
    line_number: int | None = None
    evidence: str | None = None
    explanation: str | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "module": self.module,
            "rule_id": self.rule_id,
            "category": self.category,
            "severity": self.severity,
            "confidence": self.confidence,
            "score_contribution": self.score_contribution,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "evidence": self.evidence,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
        }


@dataclass
class ScanResult:
    package_name: str | None = None
    decision: str = "ALLOW"
    score: int = 0
    findings: list[Finding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    name_similarity: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    scanner_version: str = "0.1.0"
    rule_set_version: str = "baseline-0.1"
    configuration_version: str = "baseline-0.1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_name": self.package_name,
            "decision": self.decision,
            "score": self.score,
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
            "name_similarity": self.name_similarity,
            "summary": self.summary,
            "scanner_version": self.scanner_version,
            "rule_set_version": self.rule_set_version,
            "configuration_version": self.configuration_version,
        }
