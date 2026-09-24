"""Static analysis of installation and build files."""

from __future__ import annotations

from pathlib import Path

from supplyguard.models import Finding


def analyze_install_files(file_paths: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for file_path in file_paths:
        lower_name = Path(file_path).name.lower()
        if lower_name not in {"setup.py", "pyproject.toml", "setup.cfg"}:
            continue
        text = Path(file_path).read_text(encoding="utf-8", errors="replace")
        markers = [
            "os.system",
            "subprocess",
            "exec(",
            "eval(",
            "create_package",
            "build_backend",
        ]
        for marker in markers:
            if marker in text:
                findings.append(
                    Finding(
                        finding_id=f"install_script::{file_path}:{marker}",
                        module=Path(file_path).name,
                        rule_id="INSTALL_SCRIPT_SUSPICIOUS",
                        category="build_script",
                        severity="MEDIUM",
                        confidence="MEDIUM",
                        score_contribution=18,
                        file_path=file_path,
                        evidence=marker,
                        explanation="The installation or build file contains code that could be used during package construction.",
                        recommendation="Review the build configuration and consider whether the package legitimately needs runtime shell execution.",
                    )
                )
                break
    return findings
