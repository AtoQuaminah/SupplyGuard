"""Reporting helpers for human-readable output."""

from __future__ import annotations

import json


def format_human_summary(result: dict[str, object]) -> str:
    findings = result.get("findings", [])
    lines = [
        f"Package: {result.get('package_name') or 'unknown'}",
        f"Decision: {result.get('decision')}",
        f"Risk Score: {result.get('score')}",
        f"Summary: {result.get('summary')}",
    ]
    if findings:
        lines.append("Findings:")
        for item in findings[:5]:
            lines.append(f"  - {item.get('rule_id')} [{item.get('severity')}] {item.get('explanation')}")
    return "\n".join(lines)


def json_dumps(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2)
