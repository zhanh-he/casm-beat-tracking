#!/usr/bin/env python3
"""Evaluate CASM on the cache format used by the eight-fold experiments."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import mir_eval
import numpy as np

from casm_beat_tracking import CASMConfig, CASMDecoder

METRICS = ("fmeasure", "cmlt", "amlt")


def metrics(truth: np.ndarray, estimate: np.ndarray, trim: float) -> dict[str, float]:
    truth = mir_eval.beat.trim_beats(truth, min_beat_time=trim)
    estimate = mir_eval.beat.trim_beats(estimate, min_beat_time=trim)
    if not len(truth):
        return {name: math.nan for name in METRICS}
    fmeasure = mir_eval.beat.f_measure(truth, estimate)
    _, cmlt, _, amlt = mir_eval.beat.continuity(truth, estimate)
    return {"fmeasure": float(fmeasure), "cmlt": float(cmlt), "amlt": float(amlt)}


def infer_fold(path: Path) -> int | None:
    """Infer one fold number from names such as ``fold0_val`` or ``fold_0``."""
    matches = {
        int(match)
        for match in re.findall(
            r"(?:^|[/_-])fold[_-]?([0-7])(?=[/_-]|$)", path.as_posix().lower()
        )
    }
    if len(matches) > 1:
        raise ValueError(f"ambiguous fold in path: {path}")
    return next(iter(matches)) if matches else None


def evaluate(
    path: Path, decoder: CASMDecoder, trim: float, fold: int | None
) -> dict[str, object]:
    with np.load(path, allow_pickle=False) as item:
        beats, downbeats = decoder.decode(item["beat_logits"], item["downbeat_logits"])
        row: dict[str, object] = {
            "piece": str(item["piece"]),
            "dataset": str(item["dataset"]),
            "fold": fold,
        }
        for name, value in metrics(item["truth_beat"], beats, trim).items():
            row[f"beat_{name}"] = value
        if bool(item["has_downbeats"]):
            downbeat_metrics = metrics(item["truth_downbeat"], downbeats, trim)
        else:
            downbeat_metrics = {name: math.nan for name in METRICS}
        for name, value in downbeat_metrics.items():
            row[f"downbeat_{name}"] = value
    return row


def mean(values: list[object]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return sum(finite) / len(finite) if finite else math.nan


def aggregate(rows: list[dict[str, object]]) -> dict[str, object]:
    numeric = [
        name for name in rows[0] if name not in {"piece", "dataset", "fold"}
    ]
    by_dataset: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_fold: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_dataset[str(row["dataset"])].append(row)
        if row["fold"] is not None:
            by_fold[int(row["fold"])].append(row)

    def summarize(group: list[dict[str, object]]) -> dict[str, float]:
        return {name: mean([row[name] for row in group]) for name in numeric}

    return {
        "piece_count": len(rows),
        "macro_piece": summarize(rows),
        "per_dataset": {
            name: summarize(group) for name, group in sorted(by_dataset.items())
        },
        "per_fold": {
            str(fold): summarize(group) for fold, group in sorted(by_fold.items())
        },
    }


def json_safe(value: object) -> object:
    """Convert non-finite metric sentinels to strict-JSON strings."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return "nan"
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", action="append", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--trim-seconds", type=float, default=5.0)
    args = parser.parse_args()

    config = CASMConfig.from_json(args.config) if args.config else CASMConfig()
    decoder = CASMDecoder(config)
    sources: list[tuple[Path, int | None]] = []
    for directory in args.cache_dir:
        paths = sorted(directory.glob("*.npz"))
        if not paths:
            raise SystemExit(f"no .npz cache files found in {directory}")
        fold = infer_fold(directory)
        sources.extend((path, fold) for path in paths)
    rows = [
        evaluate(path, decoder, args.trim_seconds, fold) for path, fold in sources
    ]
    rows.sort(
        key=lambda row: (
            -1 if row["fold"] is None else int(row["fold"]),
            str(row["dataset"]),
            str(row["piece"]),
        )
    )
    pieces = [str(row["piece"]) for row in rows]
    if len(pieces) != len(set(pieces)):
        raise SystemExit("duplicate piece identifiers across cache directories")

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    with args.output_prefix.with_suffix(".pieces.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    args.output_prefix.with_suffix(".summary.json").write_text(
        json.dumps(
            json_safe(aggregate(rows)), indent=2, sort_keys=True, allow_nan=False
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
