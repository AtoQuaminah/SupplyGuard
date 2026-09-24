"""Run a minimal inert evaluation over the bundled sample dataset."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from supplyguard.scanner import scan_file


def _ensure_zip(sample_dir: Path, source_path: Path) -> Path:
    archive_path = sample_dir / f"{source_path.stem}.zip"
    if not archive_path.exists():
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(source_path, arcname=source_path.name)
    return archive_path


def _scan_sample(path: Path) -> dict[str, object]:
    return scan_file(str(path))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / "datasets" / "samples" / "manifest.json").read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for class_name, config in manifest["classes"].items():
        sample_dir = root / "datasets" / "samples" / config["path"]
        for file_path in sorted(sample_dir.glob("*.py")):
            archive_path = _ensure_zip(sample_dir, file_path)
            result = _scan_sample(archive_path)
            rows.append({
                "sample": archive_path.name,
                "label": config["label"],
                "decision": result["decision"],
                "score": result["score"],
                "findings": len(result["findings"]),
            })
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
