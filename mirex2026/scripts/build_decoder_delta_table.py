#!/usr/bin/env python3
"""Rebuild the historical Direct-baseline table from frozen source CSVs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "target_table_20261005"
PLPDP_SOURCE = ROOT / "results" / "plpdp_default_20261007" / "raw"
SOURCES = {
    "target_comparison_beatthis_split.csv":
        "64758983f238b1a62da9292ef7e2fbb64b7cd1585557bbd8163e69c6c140f732",
    "target_comparison_beatthis_full_and_baselines.csv":
        "92fbd5106eba07d02ad81545f81ef2d55d6dceb8e7758736791babc47e44bfcf",
    "target_comparison_mscnn_tcn.csv":
        "f36c64aecb367d143d815df2c2e144203af4d58db2c495ae38e8f175a64a5b4a",
}
METHODS = (
    ("direct", "Direct (absolute)"),
    ("casm_no_smc", "CASM Δ"),
    ("dbn_default", "DBN 55–215 Δ"),
    ("dbn_30_300", "DBN 30–300 Δ"),
    ("plpdp", "PLPDP Δ"),
)
PLPDP_INPUTS = {
    "winner_single_split": ("beatthis_split", "5dcf1070f3fef5a10f37e886914d8532e555f294ca82a092a86650dfbf50b64d", "811ca98ee917cad5797390c6a45b85b60ffa92fb251e00b08d5d3ab2083f6a03"),
    "winner_no_smc_final": ("beatthis_full", "d93cd1dda844d99576ed8047eb69a4492ed28474839ba73bf7c2739f523ff402", "02cb00c210e8a6be50d39a19bdd72d17a2d9eae4f92841fd6b5eaab8e2078035"),
    "mscnn_split_seed0_e1499": ("mscnn_split", "4ceedfd28a661f03e215d3e7583975cb1f9584984b484a1e0a88569f257d01bc", "f97640fa6f0aecd51212db4a2c7c5db6be0c7126cf6de54788c460343f518a92"),
    "tcn_split_seed0_e119": ("tcn_split", "75626a278ff51e3c5961002d793e03f63d8c016842a962f8a1a1945efbeb51af", "778c56d0d8667a834c663bbd6960c9bca21e3f150fdacaa23cfaa8c2e9141d90"),
    "tcn_full_seed0_e120": ("tcn_full", "adb9d210908bf1a787a5f6090f41e6c06b1cc75be56f85bdc186605e4a83714e", "25a22e952b005bd2dabe23ceb55a7b77a8f3543942821e38e05fc2c5812fee55"),
}
GROUPS = (
    ("gtzan", ("beat_fmeasure", "beat_cmlt", "beat_amlt")),
    ("gtzan", ("downbeat_fmeasure", "downbeat_cmlt", "downbeat_amlt")),
    ("smc", ("beat_fmeasure", "beat_cmlt", "beat_amlt")),
)
CENT = Decimal("0.01")


@dataclass(frozen=True)
class Model:
    source_id: str
    label: str
    training: str


MODELS = (
    Model("winner_single_split", "BeatThis seed-2 e119", "3,783 log-Mel; 556 allowed validation"),
    Model("winner_no_smc_final", "BeatThis seed-2 e120, full retrain", "4,339 log-Mel; no held-out validation"),
    Model("mscnn_split_seed0_e1499", "MSCNN seed-0 e1499", "3,783 log-Mel; 556 allowed validation"),
    Model("tcn_split_seed0_e119", "TCN seed-0 e119", "3,783 log-Mel; 556 allowed validation"),
    Model("tcn_full_seed0_e120", "TCN seed-0 e120, full retrain", "4,339 log-Mel; no held-out validation"),
)
PLACEHOLDERS = (
    ("MSCNN seed-0 e1500, full retrain incomplete", "4,339 log-Mel; no held-out validation"),
    ("BeatFM e15, stopped", "911 mapped WAVs: 774 train + 137 validation"),
    ("BeatFM expanded, stopped", "1,684 mapped WAVs: 1,431 train + 253 validation"),
    ("SpecTNT placeholder", "not implemented"),
)


def rounded_percent(value: str) -> Decimal:
    if not value:
        raise ValueError("missing metric in a required result row")
    return (Decimal(value) * 100).quantize(CENT, rounding=ROUND_HALF_UP)


def load_rows() -> dict[tuple[str, str, str], dict[str, str]]:
    rows: dict[tuple[str, str, str], dict[str, str]] = {}
    wanted = {model.source_id for model in MODELS}
    for name, expected_sha in SOURCES.items():
        path = SOURCE / name
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            raise ValueError(f"source hash mismatch: {path}")
        with path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                if row["model_id"] not in wanted:
                    continue
                if row["smc_training_status"] != "excluded":
                    raise ValueError(f"forbidden SMC-trained model: {row['model_id']}")
                key = (row["model_id"], row["dataset"], row["method"])
                if key in rows:
                    raise ValueError(f"duplicate result grain: {key}")
                if row["dataset"] not in ("gtzan", "smc"):
                    raise ValueError(f"unexpected dataset: {key}")
                expected_pieces = "993" if row["dataset"] == "gtzan" else "217"
                if row["pieces"] != expected_pieces:
                    raise ValueError(f"unexpected piece count: {key}")
                rows[key] = row
    for model_id, (stem, summary_sha, pieces_sha) in PLPDP_INPUTS.items():
        summary_path = PLPDP_SOURCE / f"{stem}_plpdp.summary.json"
        pieces_path = PLPDP_SOURCE / f"{stem}_plpdp.pieces.csv"
        for path, expected_sha in ((summary_path, summary_sha), (pieces_path, pieces_sha)):
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha:
                raise ValueError(f"PLPDP source hash mismatch: {path}")
        summary = json.loads(summary_path.read_text())
        with pieces_path.open(newline="") as handle:
            piece_rows = list(csv.DictReader(handle))
        counts = Counter(row["dataset"] for row in piece_rows)
        identities = {(row["dataset"], row["piece"]) for row in piece_rows}
        if (summary["piece_count"] != 1210 or counts != {"gtzan": 993, "smc": 217}
                or len(identities) != 1210):
            raise ValueError(f"invalid PLPDP piece coverage: {model_id}")
        for dataset in ("gtzan", "smc"):
            metrics = GROUPS[0][1] + (GROUPS[1][1] if dataset == "gtzan" else ())
            source_metrics = summary["per_dataset"][dataset]
            for metric in metrics:
                values = [float(row[metric]) for row in piece_rows if row["dataset"] == dataset]
                if not all(map(math.isfinite, values)) or not math.isclose(
                    statistics.fmean(values), float(source_metrics[metric]), abs_tol=1e-12
                ):
                    raise ValueError(f"PLPDP aggregate mismatch: {model_id}/{dataset}/{metric}")
            rows[(model_id, dataset, "plpdp")] = {
                "model_id": model_id, "dataset": dataset, "method": "plpdp",
                "pieces": str(counts[dataset]), "smc_training_status": "excluded",
                **{metric: str(source_metrics[metric]) for metric in metrics},
            }
    expected = {
        (model.source_id, dataset, method)
        for model in MODELS
        for dataset in ("gtzan", "smc")
        for method, _ in METHODS
    }
    if set(rows) != expected:
        raise ValueError(f"missing/unexpected result rows: {expected ^ set(rows)}")
    return rows


def render_cell(
    rows: dict[tuple[str, str, str], dict[str, str]],
    model_id: str,
    dataset: str,
    metrics: tuple[str, str, str],
    method: str,
) -> str:
    absolute = {
        key: tuple(rounded_percent(rows[(model_id, dataset, key)][metric]) for metric in metrics)
        for key, _ in METHODS
    }
    best = tuple(max(values[i] for values in absolute.values()) for i in range(3))
    baseline = absolute["direct"]
    values = absolute[method]
    formatted = []
    for i, value in enumerate(values):
        if method == "direct":
            shown = f"{value:.2f}"
        else:
            difference = value - baseline[i]
            shown = f"{difference:+.2f}" if difference else "0.00"
        formatted.append(f"**{shown}**" if value == best[i] else shown)
    return " / ".join(formatted)


def build_table() -> str:
    rows = load_rows()
    lines = [
        "| Model weight | Training data | Decoder | GTZAN beat F / CMLt / AMLt | GTZAN downbeat F / CMLt / AMLt | SMC beat F / CMLt / AMLt |",
        "|---|---|---|---:|---:|---:|",
    ]
    for model in MODELS:
        for index, (method, method_label) in enumerate(METHODS):
            cells = [
                render_cell(rows, model.source_id, dataset, metrics, method)
                for dataset, metrics in GROUPS
            ]
            lines.append(
                f"| {model.label if index == 0 else ''} | "
                f"{model.training if index == 0 else ''} | {method_label} | "
                + " | ".join(cells) + " |"
            )
    for label, training in PLACEHOLDERS:
        lines.append(f"| {label} | {training} | — | — | — | — |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(build_table(), end="")
