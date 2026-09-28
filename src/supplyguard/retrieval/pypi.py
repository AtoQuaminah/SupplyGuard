"""Retrieval code for package artifacts without installing them."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from supplyguard.exceptions import RetrievalError


def get_package_artifact(package_name: str, destination: str | None = None) -> tuple[str, str | None]:
    normalized = package_name.strip()
    if not normalized:
        raise RetrievalError("Empty package name")
    url = f"https://pypi.org/pypi/{normalized}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # pragma: no cover - network dependent in CI
        raise RetrievalError(f"PyPI unavailable: {exc}") from exc

    releases = payload.get("releases", {})
    latest_version = payload.get("info", {}).get("version")
    version_names = [latest_version] if latest_version in releases else []
    version_names.extend(
        version_name
        for version_name in sorted(releases, key=lambda item: item, reverse=True)
        if version_name not in version_names
    )
    selected = None
    for version_name in version_names:
        for file_info in releases.get(version_name, []):
            if file_info.get("packagetype") in {"sdist", "bdist_wheel"}:
                selected = file_info
                break
        if selected:
            break
    if selected is None:
        raise RetrievalError(f"No supported artifact found for {normalized}")

    artifact_url = selected.get("url")
    if not artifact_url:
        raise RetrievalError(f"Artifact URL missing for {normalized}")
    target_dir = Path(destination) if destination else Path.cwd() / "downloads"
    target_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = artifact_url.rstrip("/").split("/")[-1]
    output_path = target_dir / artifact_name
    with urllib.request.urlopen(artifact_url, timeout=10) as response, open(output_path, "wb") as handle:
        handle.write(response.read())
    return str(output_path), selected.get("packagetype")
