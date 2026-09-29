#!/usr/bin/env python3
"""Compute paired, piece-level diagnostic differences on an eligible artifact."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from evaluation_policy import eligible_datasets, load_models


def load_pieces(root: Path, model: str, method: str, dataset: str) -> dict[str, dict[str, str]]:
    path = root / "raw" / model / f"{method}.pieces.csv"
    with path.open(newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["dataset"] == dataset]
    pieces = {row["piece"]: row for row in rows}
    if len(pieces) != len(rows):
        raise ValueError(f"duplicate piece ids in {path}")
    return pieces


def paired_difference(
    root: Path,
    lhs: tuple[str, str],
    rhs: tuple[str, str],
    dataset: str,
    metric: str,
    rng: np.random.Generator,
) -> dict[str, object]:
    left = load_pieces(root, *lhs, dataset)
    right = load_pieces(root, *rhs, dataset)
    if set(left) != set(right):
        raise ValueError(f"piece panel differs for {lhs} and {rhs} on {dataset}")
    differences = np.asarray(
        [float(left[piece][metric]) - float(right[piece][metric]) for piece in sorted(left)],
        dtype=np.float64,
    )
    if not np.all(np.isfinite(differences)):
        raise ValueError(f"nonfinite paired difference for {dataset} {metric}")
    indices = rng.integers(0, len(differences), size=(10_000, len(differences)))
    means = differences[indices].mean(axis=1)
    return {
        "lhs": "/".join(lhs),
        "rhs": "/".join(rhs),
        "dataset": dataset,
        "metric": metric,
        "pieces": len(differences),
        "mean_difference": float(differences.mean()),
        "bootstrap_95_percent_interval": [float(x) for x in np.quantile(means, [0.025, 0.975])],
        "bootstrap_seed": 20260929,
        "bootstrap_resamples": 10_000,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    root = args.artifact.resolve()
    if not (root / "COMPLETE").is_file():
        raise SystemExit("artifact is not complete")
    models = {row["model_id"]: row for row in load_models(root / "manifest" / "models.tsv")}
    if "smc" in eligible_datasets(models["official_final0"]):
        raise SystemExit("official final0 is unexpectedly eligible for SMC")
    rng = np.random.default_rng(20260929)
    comparisons: list[dict[str, object]] = []
    ours = "ours_no_smc_seed0_e100"
    for dataset in ("smc", "gtzan"):
        metrics = ["beat_fmeasure", "beat_cmlt", "beat_amlt"]
        if dataset == "gtzan":
            metrics += ["downbeat_fmeasure", "downbeat_cmlt", "downbeat_amlt"]
        for metric in metrics:
            comparisons.append(
                paired_difference(root, (ours, "casm_no_smc"), (ours, "direct"), dataset, metric, rng)
            )
            comparisons.append(
                paired_difference(root, (ours, "dbn_default"), (ours, "direct"), dataset, metric, rng)
            )
        if dataset == "gtzan":
            for metric in metrics:
                comparisons.append(
                    paired_difference(
                        root, (ours, "direct"), ("official_final0", "direct"), dataset, metric, rng
                    )
                )
    print(json.dumps({"scope": "diagnostic only; no model selection", "comparisons": comparisons}, indent=2))


if __name__ == "__main__":
    main()
