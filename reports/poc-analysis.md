# SupplyGuard Proof-of-Concept Analysis

Run time (UTC): 2026-09-30T12:45:56.605683+00:00
Scanner: 0.1.0 (rules baseline-0.1, config baseline-0.1)
Environment: Python 3.14.7 on Windows-11-10.0.26200-SP0
Git revision: a4570b5
Source working-tree changes: none

## Synthetic labeled benchmark

Scanned 39 archives; 39 had binary labels.
A prediction is considered risky when the decision is WARN or BLOCK.

TP 17 | TN 17 | FP 0 | FN 5
Precision 1.000 | Recall 0.773 | FPR 0.000 | F1 0.872
Per-archive scan time: mean 0.0027s, median 0.0021s, p95 0.0059s.

## Real-world PyPI package run

Requested 9 packages; scanned 9; errors 0.
Successful artifacts totaled 1142937 bytes.
End-to-end retrieval plus scan: mean 0.872s, median 0.863s, p95 1.214s.
Retrieval mean 0.727s; static scan mean 0.144s.
Decision counts: ALLOW 4, BLOCK 3, WARN 2.

| Package | Artifact | Size (bytes) | Decision | Score | Findings | Retrieval (s) | Scan (s) | Status |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| click | click-8.5.0-py3-none-any.whl | 125251 | BLOCK | 320 | 8 | 1.038 | 0.131 | scanned |
| flask | flask-3.1.3-py3-none-any.whl | 103424 | BLOCK | 80 | 2 | 0.741 | 0.096 | scanned |
| idna | idna-3.20-py3-none-any.whl | 69583 | ALLOW | 0 | 0 | 0.691 | 0.094 | scanned |
| packaging | packaging-26.3-py3-none-any.whl | 129956 | BLOCK | 120 | 3 | 0.695 | 0.168 | scanned |
| pyyaml | pyyaml-6.0.3-cp310-cp310-macosx_10_13_x86_64.whl | 184227 | ALLOW | 0 | 0 | 0.800 | 0.112 | scanned |
| requests | requests-2.34.2-py3-none-any.whl | 73075 | WARN | 40 | 1 | 0.478 | 0.098 | scanned |
| rich | rich-15.0.0-py3-none-any.whl | 310654 | ALLOW | 0 | 0 | 0.789 | 0.425 | scanned |
| six | six-1.17.0-py2.py3-none-any.whl | 11050 | WARN | 40 | 1 | 0.588 | 0.034 | scanned |
| urllib3 | urllib3-2.8.0-py3-none-any.whl | 135717 | ALLOW | 0 | 0 | 0.724 | 0.142 | scanned |

## Interpretation and limitations

- Synthetic metrics measure agreement with this small, generated fixture set only; they are not estimates of production detection accuracy.
- Real PyPI packages do not have ground-truth maliciousness labels here. Decisions are scanner outputs, not verified safety verdicts.
- Several mainstream packages received WARN or BLOCK from broad execution-related rules. Treat these as triage alerts; this run does not establish maliciousness and suggests the rules may be noisy.
- Packages were downloaded as archives and scanned as data. Nothing was installed, imported, or executed.
- Retrieval latency includes PyPI metadata and artifact download. Scan latency covers local archive validation, extraction, and static analysis.
- Results reflect the current proof-of-concept rules and current PyPI artifacts at run time; they are not a controlled multi-run benchmark.
