"""Metadata extraction helpers for a package artifact."""

from __future__ import annotations

from pathlib import Path


def extract_metadata(root_path: str) -> dict[str, object]:
    root = Path(root_path)
    metadata: dict[str, object] = {
        "name": None,
        "version": None,
        "summary": None,
        "author": None,
        "available": "NOT_AVAILABLE",
    }
    for candidate in ["PKG-INFO", "METADATA", "pyproject.toml", "setup.cfg"]:
        file_path = root / candidate
        if not file_path.exists():
            continue
        metadata["available"] = "AVAILABLE"
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if file_path.name == "pyproject.toml":
            if "name" in text:
                meta = text.split("name =")
                if len(meta) > 1:
                    metadata["name"] = meta[1].split("\n", 1)[0].strip().strip('"\'')
        else:
            for line in text.splitlines():
                for key in ("Name:", "Version:", "Summary:", "Author:"):
                    if line.startswith(key):
                        value = line.split(":", 1)[1].strip()
                        metadata[key[:-1].lower()] = value
                        break
    return metadata
