# Requirement traceability

| Requirement | Component | Implementation | Test |
| --- | --- | --- | --- |
| FR-001 | Retrieval and scanner entry points | `src/supplyguard/scanner.py`, `src/supplyguard/retrieval/pypi.py` | `tests/test_scanner.py` |
| FR-002 | Archive validation and extraction | `src/supplyguard/artifact/validation.py`, `src/supplyguard/artifact/archive.py` | `tests/test_scanner.py` |
| FR-003 | Static AST rule engine | `src/supplyguard/analysis/ast_rules.py` | `tests/test_scanner.py` |
| FR-004 | Build-file analysis | `src/supplyguard/analysis/install_analysis.py` | `tests/test_scanner.py` |
| FR-005 | Name similarity | `src/supplyguard/analysis/name_similarity.py` | `tests/test_scanner.py` |
| FR-006 | Risk scoring and decisioning | `src/supplyguard/scoring/risk.py` | `tests/test_scanner.py` |
| FR-007 | CLI | `src/supplyguard/cli.py` | `tests/integration/test_cli.py` |
| FR-008 | Documentation and auditability | `docs/*.md` | `docs/implementation-status.md` |
