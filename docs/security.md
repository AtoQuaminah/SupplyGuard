# Security model

## Trust boundary

The candidate package crosses no execution boundary inside SupplyGuard. It is processed as artifact bytes and decoded text only.

## Controls implemented

- Archive validation before extraction.
- Path normalization and resolution checks.
- Symlink rejection during tar extraction.
- Oversized archive and extraction protections.
- AST-based source analysis instead of import-based execution.
- Static inspection of `setup.py`, `pyproject.toml`, and `setup.cfg`.

## Non-execution guarantee

This proof-of-concept intentionally does not import package modules, execute Python code, call package entry points, or run installation hooks. The scanner remains passive and deterministic by design.
