"""Benchmark synthetic fixtures and real PyPI artifacts without installing them."""

from __future__ import annotations

import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from supplyguard.config import DEFAULT_CONFIG
from supplyguard.retrieval.pypi import get_package_artifact
from supplyguard.scanner import scan_file


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGES = [
    "click",
    "flask",
    "idna",
    "packaging",
    "pyyaml",
    "requests",
    "rich",
    "six",
    "urllib3",
]
DATASET_ROOTS = [ROOT / "dataset_generated", ROOT / "dataset_generated_large"]


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentile)
    return ordered[index]


def _timing_summary(values: list[float]) -> dict[str, float | None | int]:
    if not values:
        return {"count": 0, "mean_seconds": None, "median_seconds": None, "p95_seconds": None, "max_seconds": None}
    return {
        "count": len(values),
        "mean_seconds": statistics.mean(values),
        "median_seconds": statistics.median(values),
        "p95_seconds": _percentile(values, 0.95),
        "max_seconds": max(values),
    }


def _scan_synthetic() -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dataset_root in DATASET_ROOTS:
        manifest_path = dataset_root / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        classes = manifest.get("classes", {})
        for archive_path in sorted(dataset_root.rglob("*.zip")):
            relative_path = archive_path.relative_to(dataset_root)
            class_name = relative_path.parts[0]
            class_config = classes.get(class_name, {})
            started = time.perf_counter()
            result = scan_file(str(archive_path))
            elapsed = time.perf_counter() - started
            rows.append({
                "dataset": dataset_root.name,
                "dataset_version": manifest.get("dataset_version"),
                "sample": relative_path.as_posix(),
                "label": class_config.get("label"),
                "decision": result.get("decision"),
                "predicted_risky": result.get("decision") in {"WARN", "BLOCK"},
                "score": result.get("score"),
                "finding_count": len(result.get("findings", [])),
                "archive_bytes": archive_path.stat().st_size,
                "elapsed_seconds": elapsed,
            })

    labeled = [row for row in rows if row["label"] in (0, 1)]
    tp = sum(row["label"] == 1 and row["predicted_risky"] for row in labeled)
    tn = sum(row["label"] == 0 and not row["predicted_risky"] for row in labeled)
    fp = sum(row["label"] == 0 and row["predicted_risky"] for row in labeled)
    fn = sum(row["label"] == 1 and not row["predicted_risky"] for row in labeled)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return rows, {
        "samples": len(rows),
        "labeled_samples": len(labeled),
        "confusion_matrix": {"true_positive": tp, "true_negative": tn, "false_positive": fp, "false_negative": fn},
        "precision": precision,
        "recall": recall,
        "false_positive_rate": fp / (fp + tn) if fp + tn else 0.0,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "timing": _timing_summary([float(row["elapsed_seconds"]) for row in rows]),
    }


def _scan_real_packages(package_names: list[str]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="supplyguard-poc-") as temp_dir:
        for package_name in package_names:
            row: dict[str, object] = {"package": package_name}
            overall_started = time.perf_counter()
            try:
                retrieval_started = time.perf_counter()
                artifact_path, artifact_type = get_package_artifact(package_name, destination=temp_dir)
                retrieval_seconds = time.perf_counter() - retrieval_started
                scan_started = time.perf_counter()
                result = scan_file(artifact_path)
                scan_seconds = time.perf_counter() - scan_started
                row.update({
                    "artifact": Path(artifact_path).name,
                    "artifact_type": artifact_type,
                    "artifact_bytes": Path(artifact_path).stat().st_size,
                    "retrieval_seconds": retrieval_seconds,
                    "scan_seconds": scan_seconds,
                    "decision": result.get("decision"),
                    "score": result.get("score"),
                    "finding_count": len(result.get("findings", [])),
                    "finding_rules": sorted({str(item.get("rule_id")) for item in result.get("findings", [])}),
                    "summary": result.get("summary"),
                    "status": "scanned",
                })
            except Exception as exc:  # Network and unsupported artifact errors are part of the measurement.
                row.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            row["total_seconds"] = time.perf_counter() - overall_started
            rows.append(row)

    successful = [row for row in rows if row["status"] == "scanned"]
    return rows, {
        "requested_packages": len(package_names),
        "scanned_packages": len(successful),
        "errors": len(rows) - len(successful),
        "decision_counts": dict(sorted(Counter(str(row["decision"]) for row in successful).items())),
        "total_timing": _timing_summary([float(row["total_seconds"]) for row in successful]),
        "retrieval_timing": _timing_summary([float(row["retrieval_seconds"]) for row in successful]),
        "static_scan_timing": _timing_summary([float(row["scan_seconds"]) for row in successful]),
        "total_artifact_bytes": sum(int(row["artifact_bytes"]) for row in successful),
    }


def _markdown_report(report: dict[str, object]) -> str:
    synthetic = report["synthetic"]
    real = report["real_world"]
    lines = [
        "# SupplyGuard Proof-of-Concept Analysis",
        "",
        f"Run time (UTC): {report['run_at_utc']}",
        f"Scanner: {report['scanner_version']} (rules {report['rule_set_version']}, config {report['configuration_version']})",
        f"Environment: Python {report['python_version']} on {report['platform']}",
        f"Git revision: {report['git_revision'] or 'unavailable'}",
        f"Source working-tree changes: {', '.join(report['source_worktree_changes']) or 'none'}",
        "",
        "## Synthetic labeled benchmark",
        "",
        f"Scanned {synthetic['samples']} archives; {synthetic['labeled_samples']} had binary labels.",
        "A prediction is considered risky when the decision is WARN or BLOCK.",
        "",
        f"TP {synthetic['confusion_matrix']['true_positive']} | TN {synthetic['confusion_matrix']['true_negative']} | FP {synthetic['confusion_matrix']['false_positive']} | FN {synthetic['confusion_matrix']['false_negative']}",
        f"Precision {synthetic['precision']:.3f} | Recall {synthetic['recall']:.3f} | FPR {synthetic['false_positive_rate']:.3f} | F1 {synthetic['f1']:.3f}",
        f"Per-archive scan time: mean {synthetic['timing']['mean_seconds'] or 0:.4f}s, median {synthetic['timing']['median_seconds'] or 0:.4f}s, p95 {synthetic['timing']['p95_seconds'] or 0:.4f}s.",
        "",
        "## Real-world PyPI package run",
        "",
        f"Requested {real['requested_packages']} packages; scanned {real['scanned_packages']}; errors {real['errors']}.",
        f"Successful artifacts totaled {real['total_artifact_bytes']} bytes.",
        f"End-to-end retrieval plus scan: mean {real['total_timing']['mean_seconds'] or 0:.3f}s, median {real['total_timing']['median_seconds'] or 0:.3f}s, p95 {real['total_timing']['p95_seconds'] or 0:.3f}s.",
        f"Retrieval mean {real['retrieval_timing']['mean_seconds'] or 0:.3f}s; static scan mean {real['static_scan_timing']['mean_seconds'] or 0:.3f}s.",
        f"Decision counts: {', '.join(f'{decision} {count}' for decision, count in real['decision_counts'].items()) or 'none'}.",
        "",
        "| Package | Artifact | Size (bytes) | Decision | Score | Findings | Retrieval (s) | Scan (s) | Status |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in report["real_world_results"]:
        lines.append(
            f"| {row['package']} | {row.get('artifact', '')} | {row.get('artifact_bytes', '')} | {row.get('decision', '')} | {row.get('score', '')} | {row.get('finding_count', '')} | {row.get('retrieval_seconds', 0):.3f} | {row.get('scan_seconds', 0):.3f} | {row['status']} |"
        )
    lines.extend([
        "",
        "## Interpretation and limitations",
        "",
        "- Synthetic metrics measure agreement with this small, generated fixture set only; they are not estimates of production detection accuracy.",
        "- Real PyPI packages do not have ground-truth maliciousness labels here. Decisions are scanner outputs, not verified safety verdicts.",
        "- Several mainstream packages received WARN or BLOCK from broad execution-related rules. Treat these as triage alerts; this run does not establish maliciousness and suggests the rules may be noisy.",
        "- Packages were downloaded as archives and scanned as data. Nothing was installed, imported, or executed.",
        "- Retrieval latency includes PyPI metadata and artifact download. Scan latency covers local archive validation, extraction, and static analysis.",
        "- Results reflect the current proof-of-concept rules and current PyPI artifacts at run time; they are not a controlled multi-run benchmark.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", nargs="+", default=DEFAULT_PACKAGES)
    args = parser.parse_args()

    synthetic_results, synthetic_summary = _scan_synthetic()
    real_results, real_summary = _scan_real_packages(args.packages)
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    try:
        source_changes = subprocess.run(
            [
                "git", "status", "--short", "--",
                "src/supplyguard", "scripts/evaluation/run_poc_analysis.py", "tests/unit/test_retrieval.py",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        source_changes = []

    report: dict[str, object] = {
        "report_type": "proof_of_concept_performance_analysis",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "scanner_version": DEFAULT_CONFIG.scanner_version,
        "rule_set_version": DEFAULT_CONFIG.rule_set_version,
        "configuration_version": DEFAULT_CONFIG.configuration_version,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "git_revision": revision,
        "source_worktree_changes": source_changes,
        "synthetic": synthetic_summary,
        "synthetic_results": synthetic_results,
        "real_world": real_summary,
        "real_world_results": real_results,
    }
    output_dir = ROOT / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "poc-analysis.json"
    markdown_path = output_dir / "poc-analysis.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(_markdown_report(report), encoding="utf-8")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    print(f"Synthetic archives: {synthetic_summary['samples']}; PyPI packages scanned: {real_summary['scanned_packages']}/{real_summary['requested_packages']}")


if __name__ == "__main__":
    main()