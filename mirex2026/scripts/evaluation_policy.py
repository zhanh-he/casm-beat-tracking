#!/usr/bin/env python3
"""Fail closed when an evaluation panel overlaps a checkpoint's training data.

The current MIREX diagnostic manifests contain two training provenances. A
future provenance must be added here explicitly before it can be evaluated.
For cross-validation, use `assert_disjoint_pieces` on the fold's exact piece
inventories; a dataset-level declaration alone is insufficient.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DATASET_PIECES = {"smc": 217, "gtzan": 993}
MANIFEST_COLUMNS = ("model_id", "checkpoint", "smc_training_status")


def eligible_datasets(model: dict[str, str]) -> tuple[str, ...]:
    """Return only fully unseen panels; reject unknown training provenance."""
    model_id = model["model_id"]
    status = model["smc_training_status"]
    checkpoint_name = Path(model["checkpoint"]).name
    if model_id == "official_final0" or checkpoint_name == "beat_this-final0.ckpt":
        if status != "included_upstream_final0":
            raise ValueError("official final0 must declare SMC in its training pool")
    if status == "included_upstream_final0":
        return ("gtzan",)
    if status == "excluded":
        return ("smc", "gtzan")
    raise ValueError(f"unknown training provenance for {model_id}: {status!r}")


def assert_disjoint_pieces(
    train_pieces: set[str], eval_pieces: set[str], *, context: str
) -> None:
    overlap = train_pieces & eval_pieces
    if overlap:
        examples = ", ".join(sorted(overlap)[:5])
        raise ValueError(
            f"training/evaluation overlap in {context}: "
            f"{len(overlap)} piece(s), including {examples}"
        )


def load_models(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != MANIFEST_COLUMNS:
            raise ValueError(f"models TSV must have exactly {MANIFEST_COLUMNS}")
        models = list(reader)
    if not models:
        raise ValueError("models TSV is empty")
    names = [row["model_id"] for row in models]
    if len(names) != len(set(names)) or any(not name for name in names):
        raise ValueError("model ids must be unique and nonempty")
    for model in models:
        if not model["checkpoint"]:
            raise ValueError(f"missing checkpoint path for {model['model_id']}")
        eligible_datasets(model)
    return models


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=Path, required=True)
    args = parser.parse_args()
    for model in load_models(args.models):
        for dataset in eligible_datasets(model):
            print(f"{model['model_id']}\t{dataset}")


if __name__ == "__main__":
    main()
