"""Command-line interface for SupplyGuard."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

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


def _run_scan_file(path: str, json_output: bool) -> int:
    result = scan_file(path)
    if json_output:
        print(json_dumps(result))
    else:
        print(format_human_summary(result))
    return _exit_code_for(result.get("decision", "ALLOW"))


def _run_scan_package(package_name: str, json_output: bool) -> int:
    result = scan_package(package_name)
    if json_output:
        print(json_dumps(result))
    else:
        print(format_human_summary(result))
    return _exit_code_for(result.get("decision", "ALLOW"))


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
