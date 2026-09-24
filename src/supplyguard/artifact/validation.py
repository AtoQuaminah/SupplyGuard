"""Validation utilities for Package artifacts."""

from __future__ import annotations

import os
from pathlib import Path

from supplyguard.config import ScannerConfig


def validate_archive(path: str | os.PathLike[str], config: ScannerConfig) -> dict[str, object]:
    file_path = Path(path)
    if not file_path.exists():
        return {"ok": False, "error": "file_missing"}
    size = file_path.stat().st_size
    if size > config.max_archive_size_bytes:
        return {"ok": False, "error": "oversized_archive", "details": f"{size} > {config.max_archive_size_bytes}"}
    return {"ok": True, "size": size}
