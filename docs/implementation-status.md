# Implementation status

| Requirement ID | Description | Priority | Status | Implementation | Test | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| FR-001 | Accept a package name or local artifact | HIGH | IMPLEMENTED | `supplyguard/scanner.py` | `tests/test_scanner.py` | Local archive scanning is supported; PyPI retrieval is attempted when a package name is supplied. |
| FR-002 | Safe extraction and validation | HIGH | IMPLEMENTED | `supplyguard/artifact/archive.py` | `tests/test_scanner.py` | Traversal and unsafe symlink protections are enforced. |
| FR-003 | Static analysis of Python source | HIGH | IMPLEMENTED | `supplyguard/analysis/ast_rules.py` | `tests/test_scanner.py` | AST-based detection of `os.system`, `subprocess`, and `eval`-style patterns. |
| FR-004 | Install/build file analysis | MEDIUM | IMPLEMENTED | `supplyguard/analysis/install_analysis.py` | `tests/test_scanner.py` | Review of `setup.py` and project metadata files. |
| FR-005 | Name similarity analysis | MEDIUM | IMPLEMENTED | `supplyguard/analysis/name_similarity.py` | `tests/test_scanner.py` | Deterministic similarity comparison with configurable threshold. |
| FR-006 | Risk scoring and decisions | HIGH | IMPLEMENTED | `supplyguard/scoring/risk.py` | `tests/test_scanner.py` | Deterministic scoring and WARN/BLOCK decisions. |
| FR-007 | CLI integration | HIGH | IMPLEMENTED | `supplyguard/cli.py` | `tests/integration/test_cli.py` | `scan`, `scan-file`, and `version` commands are available. |
| FR-008 | Documentation and traceability | MEDIUM | IMPLEMENTED | `docs/*.md` | `docs/traceability.md` | Project requirements and implementation mapping are documented. |
