"""Safe extraction for candidate archives."""

from __future__ import annotations

import io
import os
import tarfile
import zipfile
from pathlib import Path

from supplyguard.config import ScannerConfig


def _safe_join(base_dir: Path, relative_member: str) -> Path:
    normalized = relative_member.replace('\\', '/')
    if normalized.startswith('/') or normalized.startswith('..') or '\\' in normalized:
        raise ValueError(f"Rejected traversal path: {relative_member!r}")
    candidate = (base_dir / normalized).resolve()
    base_resolved = base_dir.resolve()
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise ValueError(f"Target escapes extraction root: {relative_member!r}")
    return candidate


def extract_safe_archive(source_path: str | os.PathLike[str], destination_dir: str | os.PathLike[str], config: ScannerConfig) -> list[str]:
    source = Path(source_path)
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    issues: list[str] = []
    file_total = 0
    member_count = 0

    try:
        if zipfile.is_zipfile(source):
            with zipfile.ZipFile(source) as archive:
                for member in archive.infolist():
                    member_count += 1
                    if member_count > config.max_member_count:
                        issues.append("member_count_exceeded")
                        break
                    if member.is_dir():
                        continue
                    target_name = member.filename
                    if target_name.startswith('/') or '..' in target_name.split('/'):
                        issues.append(f"traversal_rejected::{target_name}")
                        continue
                    try:
                        target = _safe_join(destination, target_name)
                    except ValueError as exc:
                        issues.append(str(exc))
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    extracted = archive.read(member)
                    if len(extracted) > config.max_extracted_size_bytes:
                        issues.append(f"extraction_size_exceeded::{target_name}")
                        continue
                    file_total += len(extracted)
                    if file_total > config.max_extracted_size_bytes:
                        issues.append("total_extraction_size_exceeded")
                        break
                    target.write_bytes(extracted)
        elif tarfile.is_tarfile(source):
            with tarfile.open(source, "r:*") as archive:
                for member in archive.getmembers():
                    member_count += 1
                    if member_count > config.max_member_count:
                        issues.append("member_count_exceeded")
                        break
                    if member.isdir():
                        continue
                    if member.issym() or member.islnk():
                        issues.append(f"unsafe_link_rejected::{member.name}")
                        continue
                    target_name = member.name
                    if target_name.startswith('/') or '..' in target_name.split('/'):
                        issues.append(f"traversal_rejected::{target_name}")
                        continue
                    try:
                        target = _safe_join(destination, target_name)
                    except ValueError as exc:
                        issues.append(str(exc))
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        continue
                    payload = extracted.read()
                    if len(payload) > config.max_extracted_size_bytes:
                        issues.append(f"extraction_size_exceeded::{target_name}")
                        continue
                    file_total += len(payload)
                    if file_total > config.max_extracted_size_bytes:
                        issues.append("total_extraction_size_exceeded")
                        break
                    target.write_bytes(payload)
        else:
            issues.append("unsupported_archive_format")
    except (tarfile.TarError, zipfile.BadZipFile, OSError, ValueError) as exc:  # pragma: no cover
        issues.append(f"archive_error::{type(exc).__name__}:{exc}")

    return issues
