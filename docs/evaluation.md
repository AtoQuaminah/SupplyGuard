# Evaluation

## Measures available

The evaluation framework can compute:

- TP
- TN
- FP
- FN
- Recall
- Precision
- False Positive Rate
- F1
- Latency

## Implementation notes

The project provides a deterministic evaluation utility in the `scripts/evaluation` directory. Actual evaluation numbers must come from runs over a labelled dataset and should be recorded with the dataset version, scanner version, and configuration metadata.

## Reproducibility

Each scan result stores:

- scanner version
- rule set version
- configuration version
- package name or artifact name
- final decision and score
