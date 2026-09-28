"""Command-line interface for SupplyGuard."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
from typing import Callable, Sequence
from uuid import uuid4

from supplyguard import __version__
from supplyguard.scanner import scan_file, scan_package
from supplyguard.reporting.formatter import format_human_summary, json_dumps


def _exit_code_for(decision: str) -> int:
    mapping = {
        "ALLOW": 0,
        "WARN": 1,
        "BLOCK": 2,
        "UNABLE_TO_DETERMINE": 3,
        "ANALYSIS_ERROR": 4,
        "RETRIEVAL_ERROR": 5,
    }
    return mapping.get(decision, 3)


def _write_scan_log(
    scan_type: str,
    target: str,
    started_at: str,
    elapsed_seconds: float,
    result: dict[str, object],
) -> Path:
    log_dir = Path.cwd() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    safe_target = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(target).name or target).strip("._-") or "scan"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = log_dir / f"scan-{timestamp}-{safe_target}-{uuid4().hex[:8]}.json"
    log_entry = {
        "scan_type": scan_type,
        "target": target,
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "result": result,
    }
    log_path.write_text(json.dumps(log_entry, indent=2, sort_keys=True), encoding="utf-8")
    return log_path


def _run_scan(scan_type: str, target: str, json_output: bool, scan: Callable[[], dict[str, object]]) -> int:
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    result = scan()
    elapsed_seconds = time.perf_counter() - started

    try:
        log_path = _write_scan_log(scan_type, target, started_at, elapsed_seconds, result)
        log_message = f"Log file: {log_path}"
    except OSError as exc:
        log_message = f"Warning: unable to write scan log: {exc}"

    if json_output:
        print(json_dumps(result))
        print(log_message, file=sys.stderr)
    else:
        print(format_human_summary(result))
        print(log_message)
    return _exit_code_for(result.get("decision", "ALLOW"))


def _run_scan_file(path: str, json_output: bool) -> int:
    return _run_scan("scan-file", path, json_output, lambda: scan_file(path))


def _run_scan_package(package_name: str, json_output: bool) -> int:
    return _run_scan("scan", package_name, json_output, lambda: scan_package(package_name))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="supplyguard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a package name")
    scan_parser.add_argument("package")
    scan_parser.add_argument("--json", action="store_true")

    scan_file_parser = subparsers.add_parser("scan-file", help="Scan a local archive")
    scan_file_parser.add_argument("path")
    scan_file_parser.add_argument("--json", action="store_true")

    version_parser = subparsers.add_parser("version", help="Print version")
    version_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        version_result = {"version": __version__, "name": "SupplyGuard"}
        if args.json:
            print(json_dumps(version_result))
        else:
            print(f"SupplyGuard {__version__}")
        return 0

    if args.command == "scan":
        return _run_scan_package(args.package, bool(getattr(args, "json", False)))

    if args.command == "scan-file":
        return _run_scan_file(args.path, bool(getattr(args, "json", False)))

    parser.print_help()
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
