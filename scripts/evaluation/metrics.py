"""Small evaluation helper for deterministic performance metrics."""

from __future__ import annotations

import json
from pathlib import Path


def compute_confusion(values: list[dict[str, object]]) -> dict[str, int]:
    tp = tn = fp = fn = 0
    for row in values:
        actual = bool(row.get("actual"))
        predicted = bool(row.get("predicted"))
        if actual and predicted:
            tp += 1
        elif actual and not predicted:
            fn += 1
        elif not actual and predicted:
            fp += 1
        else:
            tn += 1
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def metrics_from_rows(values: list[dict[str, object]]) -> dict[str, float | int]:
    counts = compute_confusion(values)
    tp = counts["tp"]
    tn = counts["tn"]
    fp = counts["fp"]
    fn = counts["fn"]
    total = tp + tn + fp + fn
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "recall": recall,
        "precision": precision,
        "false_positive_rate": fpr,
        "f1": f1,
        "samples": total,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compute classification metrics from a JSON rows file.")
    parser.add_argument("path", nargs="?", default="dataset.json")
    args = parser.parse_args()
    dataset_path = Path(args.path)
    rows = json.loads(dataset_path.read_text(encoding="utf-8")) if dataset_path.exists() else []
    print(json.dumps(metrics_from_rows(rows), indent=2, sort_keys=True))
