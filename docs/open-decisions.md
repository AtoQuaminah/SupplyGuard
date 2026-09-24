# Open decision register

| Decision ID | Question | Why it matters | Current options | Chosen implementation | Reason | Research status | Impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OD-001 | Which package names should be treated as reference names for similarity? | Typosquatting analysis depends on reference comparison. | static built-in set; dynamic PyPI dataset; project-local curated list | static built-in set | deterministic, offline, and reproducible by default | IMPLEMENTATION BASELINE | Low |
| OD-002 | Which scoring weights should be used for findings? | Risk decisions require deterministic weights. | fixed baseline; validated weights from large-scale evaluation | fixed baseline configuration | required for reproducibility and explainability | IMPLEMENTATION BASELINE | Medium |
| OD-003 | What package types are in scope for a first proof-of-concept? | Supported artifact types affect retrieval and extraction. | sdist, wheel, local directory, git repo | zip/tar artifact and package-name retrieval | minimal implementable scope | IMPLEMENTATION BASELINE | Low |
