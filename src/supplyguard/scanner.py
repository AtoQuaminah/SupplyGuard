"""Main scanning entry points for SupplyGuard."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from supplyguard.analysis.ast_rules import analyze_python_file
from supplyguard.analysis.install_analysis import analyze_install_files
from supplyguard.analysis.metadata import extract_metadata
from supplyguard.analysis.name_similarity import analyze_name_similarity
from supplyguard.artifact.archive import extract_safe_archive
from supplyguard.artifact.validation import validate_archive
from supplyguard.config import DEFAULT_CONFIG, ScannerConfig
from supplyguard.models import Finding, ScanResult
from supplyguard.retrieval.pypi import get_package_artifact
from supplyguard.scoring.risk import compute_risk


def _as_finding_dict(finding: Finding) -> dict[str, object]:
    return finding.to_dict()


def _scan_extracted_tree(root: Path, package_name: str | None, config: ScannerConfig) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
    findings: list[dict[str, object]] = []
    install_candidates: list[str] = []
    python_files: list[str] = []
    metadata = extract_metadata(str(root))
    name_similarity = analyze_name_similarity(package_name, threshold=config.name_similarity_threshold)

    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        rel = str(path.relative_to(root))
        if path.name.lower() in {"setup.py", "pyproject.toml", "setup.cfg"}:
            install_candidates.append(str(path))
        if path.suffix == ".py":
            python_files.append(str(path))

    for file_path in python_files:
        try:
            source = Path(file_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            findings.append(
                {
                    "finding_id": f"read_error:{file_path}",
                    "module": Path(file_path).name,
                    "rule_id": "READ_ERROR",
                    "category": "analysis_error",
                    "severity": "MEDIUM",
                    "confidence": "HIGH",
                    "score_contribution": 10,
                    "file_path": file_path,
                    "line_number": None,
                    "evidence": "Failed to read file during static analysis.",
                    "explanation": "The scanner could not read the file bytes encountered in the package artifact.",
                    "recommendation": "Review the extracted artifact and verify its integrity before accepting the package.",
                }
            )
            continue
        findings.extend(_as_finding_dict(item) for item in analyze_python_file(file_path, source, config))

    findings.extend(_as_finding_dict(item) for item in analyze_install_files(install_candidates))
    return findings, metadata, name_similarity


def scan_file(path: str, config: ScannerConfig | None = None) -> dict[str, object]:
    config = config or DEFAULT_CONFIG
    root = Path(path)
    if not root.exists():
        return {
            "package_name": None,
            "decision": "ANALYSIS_ERROR",
            "score": 0,
            "findings": [],
            "metadata": {"available": "NOT_AVAILABLE"},
            "name_similarity": {"match": False},
            "summary": "Input artifact does not exist.",
            "scanner_version": config.scanner_version,
            "rule_set_version": config.rule_set_version,
            "configuration_version": config.configuration_version,
        }

    validation = validate_archive(root, config)
    if not validation.get("ok"):
        issue = validation.get("error", "validation_error")
        finding = {
            "finding_id": f"archive_validation:{issue}",
            "module": root.name,
            "rule_id": "ARCHIVE_VALIDATION",
            "category": "archive_security",
            "severity": "HIGH",
            "confidence": "HIGH",
            "score_contribution": 45,
            "file_path": str(root),
            "line_number": None,
            "evidence": str(validation.get("details", issue)),
            "explanation": "The archive failed validation before extraction and therefore was not treated as a trusted package.",
            "recommendation": "Reject the artifact and inspect the package source or build metadata before accepting it.",
        }
        return {
            "package_name": None,
            "decision": "BLOCK",
            "score": 45,
            "findings": [finding],
            "metadata": {"available": "NOT_AVAILABLE"},
            "name_similarity": {"match": False},
            "summary": f"Archive validation failed: {issue}",
            "scanner_version": config.scanner_version,
            "rule_set_version": config.rule_set_version,
            "configuration_version": config.configuration_version,
        }

    output_dir = Path(tempfile.mkdtemp(prefix="supplyguard-"))
    issues = extract_safe_archive(root, output_dir, config)
    if issues:
        finding = {
            "finding_id": "archive_security:extract",
            "module": root.name,
            "rule_id": "SAFE_EXTRACTION",
            "category": "archive_security",
            "severity": "HIGH",
            "confidence": "HIGH",
            "score_contribution": 55,
            "file_path": str(root),
            "line_number": None,
            "evidence": "; ".join(issues[:5]),
            "explanation": "The archive contained extraction hazards such as traversal, symlinks, or size overflows and was blocked.",
            "recommendation": "Reject the archive rather than extracting it into a trusted workspace.",
        }
        return {
            "package_name": None,
            "decision": "BLOCK",
            "score": 55,
            "findings": [finding],
            "metadata": {"available": "NOT_AVAILABLE"},
            "name_similarity": {"match": False},
            "summary": "Archive extraction was blocked by traversal or security validation checks.",
            "scanner_version": config.scanner_version,
            "rule_set_version": config.rule_set_version,
            "configuration_version": config.configuration_version,
        }

    findings, metadata, name_similarity = _scan_extracted_tree(output_dir, root.stem, config)
    risk_score, decision = compute_risk(findings, metadata=metadata, name_similarity=name_similarity, config=config)
    summary = f"Scanned {root.name} with final decision {decision} and score {risk_score}."
    result = {
        "package_name": root.stem,
        "decision": decision,
        "score": risk_score,
        "findings": findings,
        "metadata": metadata,
        "name_similarity": name_similarity,
        "summary": summary,
        "scanner_version": config.scanner_version,
        "rule_set_version": config.rule_set_version,
        "configuration_version": config.configuration_version,
    }
    return result


def scan_package(package_name: str, config: ScannerConfig | None = None) -> dict[str, object]:
    config = config or DEFAULT_CONFIG
    try:
        artifact_path, _ = get_package_artifact(package_name, destination="downloads")
    except Exception as exc:  # pragma: no cover - network dependent
        return {
            "package_name": package_name,
            "decision": "UNABLE_TO_DETERMINE",
            "score": 0,
            "findings": [{
                "finding_id": "retrieval_error",
                "module": "retrieval",
                "rule_id": "RETRIEVAL_ERROR",
                "category": "retrieval",
                "severity": "MEDIUM",
                "confidence": "HIGH",
                "score_contribution": 0,
                "file_path": None,
                "line_number": None,
                "evidence": str(exc),
                "explanation": "The package could not be fetched without installing or executing code.",
                "recommendation": "Check the package name and network availability or provide a local artifact path.",
            }],
            "metadata": {"available": "NOT_AVAILABLE"},
            "name_similarity": {"match": False},
            "summary": f"Unable to retrieve {package_name} from the configured package source.",
            "scanner_version": config.scanner_version,
            "rule_set_version": config.rule_set_version,
            "configuration_version": config.configuration_version,
        }

    return scan_file(artifact_path, config=config)
