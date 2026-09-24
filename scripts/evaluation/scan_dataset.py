"""Scan all generated dataset archives and write a structured JSON summary.

This script is intentionally static-only: it reads zip archives, analyzes them as
untrusted data, and records the decision, score, and findings for every sample.
"""

from __future__ import annotations

import json
from pathlib import Path

from supplyguard.scanner import scan_file


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOTS = [
    ROOT / "dataset_generated",
    ROOT / "dataset_generated_large",
]


def iter_archives(root: Path):
    if not root.exists():
        return []
    return sorted(root.rglob("*.zip"))


def main() -> None:
    rows = []
    for dataset_root in DATASET_ROOTS:
        if not dataset_root.exists():
            continue
        manifest_path = dataset_root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        classes = manifest.get("classes", {})

        for archive_path in iter_archives(dataset_root):
            result = scan_file(str(archive_path))
            rel = archive_path.relative_to(dataset_root)
            class_name = rel.parts[0] if rel.parts else "unknown"
            label = classes.get(class_name, {}).get("label", -1)
            row = {
                "dataset": dataset_root.name,
                "class": class_name,
                "sample": archive_path.name,
                "label": label,
                "decision": result["decision"],
                "score": result["score"],
                "finding_count": len(result.get("findings", [])),
                "summary": result.get("summary"),
            }
            rows.append(row)

    output_path = ROOT / "dataset_scan_summary.json"
    output_path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(rows, indent=2, sort_keys=True))
    print(f"\nSummary written to: {output_path}")


if __name__ == "__main__":
    main()
