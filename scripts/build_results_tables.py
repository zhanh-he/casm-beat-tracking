#!/usr/bin/env python3
"""Validate the locked 7F evaluation and rebuild the public result tables."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_HASH = "93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de"
PROTOCOL_HASH = "9b9e84109178a998f9c9215244c7eee2be1b4d1c1bf4b25d93147c462668fae3"
BUNDLE = (
    ROOT
    / "self-run-figures/figure2-20260901-1200/data/full_raw_archive"
    / "qa_staging/bundle"
)
LOCKED = BUNDLE / "selected_oof_candidates" / CANDIDATE_HASH
SELECTION = BUNDLE / "formal/searches/7f_1_2_3_4_5_6_7/selection.json"
CONFIG = ROOT / "config/casm-7f-default.json"
RESULTS = ROOT / "results"

METRICS = (
    "beat_fmeasure",
    "beat_cmlt",
    "beat_amlt",
    "downbeat_fmeasure",
    "downbeat_cmlt",
    "downbeat_amlt",
)
BEAT_METRICS = METRICS[:3]
DOWNBEAT_METRICS = METRICS[3:]
DISPLAY_NAMES = {
    "asap": "ASAP",
    "ballroom": "Ballroom",
    "beatles": "Beatles",
    "candombe": "Candombe",
    "filosax": "Filosax",
    "groove_midi": "Groove MIDI",
    "guitarset": "GuitarSet",
    "hainsworth": "Hainsworth",
    "harmonix": "Harmonix",
    "hjdb": "HJDB",
    "jaah": "JAAH",
    "rwc_classical": "RWC Classical",
    "rwc_jazz": "RWC Jazz",
    "rwc_popular": "RWC Popular",
    "rwc_royalty-free": "RWC Royalty-Free",
    "simac": "Simac",
    "smc": "SMC",
    "tapcorrect": "TapCorrect",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, object] = {
                "piece": raw["piece"],
                "dataset": raw["dataset"],
                "fold": int(raw["fold"]),
            }
            row.update({metric: float(raw[metric]) for metric in METRICS})
            rows.append(row)
    return rows


def finite_values(rows: Iterable[dict[str, object]], metric: str) -> list[float]:
    values = [float(row[metric]) for row in rows]
    return [value for value in values if math.isfinite(value)]


def aggregate(rows: list[dict[str, object]]) -> dict[str, float | int]:
    result: dict[str, float | int] = {
        "beat_piece_count": len(rows),
        "downbeat_piece_count": len(finite_values(rows, "downbeat_fmeasure")),
    }
    for metric in METRICS:
        values = finite_values(rows, metric)
        result[metric] = statistics.fmean(values) if values else math.nan
    return result


def assert_close(actual: float, expected: object, label: str) -> None:
    if isinstance(expected, str) and expected.lower() == "nan":
        assert math.isnan(actual), f"{label}: expected NaN, got {actual}"
        return
    assert math.isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12), (
        f"{label}: {actual} != {expected}"
    )


def validate(rows: list[dict[str, object]]) -> dict:
    summary = load_json(LOCKED / "summary.json")
    selection = load_json(SELECTION)
    config = load_json(CONFIG)

    assert (LOCKED / "COMPLETE").exists(), "locked evaluation lacks COMPLETE marker"
    assert summary["parameter_hash"] == CANDIDATE_HASH
    assert selection["selected_candidate_hash"] == CANDIDATE_HASH
    assert selection["protocol_hash"] == PROTOCOL_HASH
    assert config["candidate_hash"] == CANDIDATE_HASH
    assert config["protocol_hash"] == PROTOCOL_HASH
    assert config["calibration_folds"] == [1, 2, 3, 4, 5, 6, 7]
    assert config["parameters"] == selection["selected_parameters"]
    assert config["parameters"] == summary["parameters"]

    assert len(rows) == summary["piece_count"] == 4556
    assert len({str(row["piece"]) for row in rows}) == len(rows), "duplicate pieces"
    assert {int(row["fold"]) for row in rows} == set(range(8))
    assert set(DISPLAY_NAMES) == {str(row["dataset"]) for row in rows}

    for row in rows:
        for metric in METRICS:
            value = float(row[metric])
            assert math.isnan(value) or 0.0 <= value <= 1.0, (
                f"out-of-range {metric} for {row['piece']}: {value}"
            )

    missing_downbeats = {
        str(row["dataset"])
        for row in rows
        if not math.isfinite(float(row["downbeat_fmeasure"]))
    }
    assert missing_downbeats == {"simac", "smc"}
    assert all(
        all(math.isnan(float(row[metric])) for metric in DOWNBEAT_METRICS)
        for row in rows
        if str(row["dataset"]) in missing_downbeats
    )

    overall = aggregate(rows)
    for metric in METRICS:
        assert_close(float(overall[metric]), summary["macro_piece"][metric], metric)

    smc_rows = [row for row in rows if row["dataset"] == "smc"]
    smc = aggregate(smc_rows)
    assert len(smc_rows) == summary["smc_piece_count"] == 217
    for metric in METRICS:
        assert_close(float(smc[metric]), summary["smc_macro_piece"][metric], f"smc {metric}")

    for fold in range(8):
        fold_rows = [row for row in rows if row["fold"] == fold]
        fold_summary = aggregate(fold_rows)
        for metric in METRICS:
            assert_close(
                float(fold_summary[metric]), summary["per_fold"][str(fold)][metric],
                f"fold {fold} {metric}",
            )
    return summary


def write_dataset_csv(groups: dict[str, list[dict[str, object]]]) -> None:
    fields = ["dataset", "beat_piece_count", "downbeat_piece_count", *METRICS]
    with (RESULTS / "beat_this_8fold_7f_by_dataset.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for dataset in DISPLAY_NAMES:
            writer.writerow({"dataset": dataset, **aggregate(groups[dataset])})
        rwc_rows = [
            row
            for dataset, rows in groups.items()
            if dataset.startswith("rwc_")
            for row in rows
        ]
        writer.writerow({"dataset": "rwc_all", **aggregate(rwc_rows)})
        all_rows = [row for rows in groups.values() for row in rows]
        writer.writerow({"dataset": "all", **aggregate(all_rows)})


def smc_fold_rows(rows: list[dict[str, object]]) -> list[dict[str, float | int]]:
    output: list[dict[str, float | int]] = []
    for fold in range(8):
        selected = [row for row in rows if row["dataset"] == "smc" and row["fold"] == fold]
        agg = aggregate(selected)
        output.append(
            {
                "fold": fold,
                "piece_count": len(selected),
                **{metric: agg[metric] for metric in BEAT_METRICS},
            }
        )
    return output


def write_smc_csv(folds: list[dict[str, float | int]]) -> None:
    fields = ["fold", "piece_count", *BEAT_METRICS]
    with (RESULTS / "beat_this_smc_7f_by_fold.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(folds)


def pct(value: float | int) -> str:
    return "—" if not math.isfinite(float(value)) else f"{100.0 * float(value):.1f}"


def result_table(groups: dict[str, list[dict[str, object]]]) -> str:
    header = (
        "| Dataset | Beat N | Beat F | Beat CMLt | Beat AMLt | "
        "Downbeat N | Downbeat F | Downbeat CMLt | Downbeat AMLt |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    )
    lines = [header]
    for dataset, display in DISPLAY_NAMES.items():
        agg = aggregate(groups[dataset])
        lines.append(
            f"| {display} | {agg['beat_piece_count']} | {pct(agg['beat_fmeasure'])} | "
            f"{pct(agg['beat_cmlt'])} | {pct(agg['beat_amlt'])} | "
            f"{agg['downbeat_piece_count'] or '—'} | {pct(agg['downbeat_fmeasure'])} | "
            f"{pct(agg['downbeat_cmlt'])} | {pct(agg['downbeat_amlt'])} |"
        )

    rwc_rows = [
        row
        for dataset, rows in groups.items()
        if dataset.startswith("rwc_")
        for row in rows
    ]
    all_rows = [row for rows in groups.values() for row in rows]
    for display, selected in (("**RWC (all)**", rwc_rows), ("**All pieces**", all_rows)):
        agg = aggregate(selected)
        lines.append(
            f"| {display} | {agg['beat_piece_count']} | {pct(agg['beat_fmeasure'])} | "
            f"{pct(agg['beat_cmlt'])} | {pct(agg['beat_amlt'])} | "
            f"{agg['downbeat_piece_count']} | {pct(agg['downbeat_fmeasure'])} | "
            f"{pct(agg['downbeat_cmlt'])} | {pct(agg['downbeat_amlt'])} |"
        )
    return "\n".join(lines)


def smc_table(folds: list[dict[str, float | int]]) -> tuple[str, dict[str, tuple[float, float]]]:
    lines = [
        "| Fold | N | Beat F | Beat CMLt | Beat AMLt |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in folds:
        lines.append(
            f"| {row['fold']} | {row['piece_count']} | {pct(row['beat_fmeasure'])} | "
            f"{pct(row['beat_cmlt'])} | {pct(row['beat_amlt'])} |"
        )
    stats = {
        metric: (
            statistics.fmean(float(row[metric]) for row in folds),
            statistics.stdev(float(row[metric]) for row in folds),
        )
        for metric in BEAT_METRICS
    }
    lines.append(
        "| **Mean ± SD** | — | "
        + " | ".join(
            f"**{100 * stats[metric][0]:.1f} ± {100 * stats[metric][1]:.1f}**"
            for metric in BEAT_METRICS
        )
        + " |"
    )
    return "\n".join(lines), stats


def write_results_doc(
    groups: dict[str, list[dict[str, object]]],
    folds: list[dict[str, float | int]],
) -> None:
    dataset_table = result_table(groups)
    fold_table, _ = smc_table(folds)
    content = f"""# Results

## Beat This backbone: locked 7F eight-fold evaluation

These are piece-macro results for the selected 7F CASM calibration on all eight backbone-held-out partitions. Folds 1–7 informed decoder selection and fold 0 did not, so this is out-of-fold with respect to backbone training but not a nested estimate of decoder calibration. Metrics are shown as percentages. Downbeat metrics are unavailable for Simac and SMC because their Beat This annotation files do not contain beat-position labels.

{dataset_table}

The source is the locked 4,556-piece evaluation for candidate `{CANDIDATE_HASH}`. The machine-readable table is [`../results/beat_this_8fold_7f_by_dataset.csv`](../results/beat_this_8fold_7f_by_dataset.csv), and [`../scripts/build_results_tables.py`](../scripts/build_results_tables.py) validates and rebuilds both files.

## SMC fold variation

{fold_table}

“Mean ± SD” is the unweighted mean and sample standard deviation across the eight held-out **fold-level piece macros**. It describes cross-fold variation, not repeated-training uncertainty. The 217-piece macro (which weights pieces equally rather than folds equally) is Beat F 62.9, CMLt 53.7, and AMLt 63.5.

## GTZAN status

The currently preserved 7F `final1` evaluation is a single post-hoc-selected point: Beat F 89.5, CMLt 81.1, AMLt 90.6; Downbeat F 79.1, CMLt 71.5, AMLt 85.3. It is **not** reported as mean ± standard deviation because it is one checkpoint selected using GTZAN Beat F and therefore is not a clean independent test estimate.

A publishable GTZAN mean ± standard deviation requires the frozen 7F decoder to be rerun on `final0`, `final1`, and `final2` without selecting on GTZAN. That refresh is intentionally pending while Kaya is under maintenance; no historical non-7F results have been relabelled as final 7F results.

## Backbone release matrix

| Backbone | Eight-fold 7F results | GTZAN mean ± SD | Checkpoints |
|---|---|---|---|
| Beat This | Validated above | Pending three-seed refresh | `final0`–`final2` and fold0–fold7 protected |
| MSCNN-lite | Pending cache recreation; the eight-fold activation cache was purged | Pending three-seed refresh | Three selected checkpoints protected |
| TCN | Pending frozen-7F refresh | Pending recovery/retraining | `final0` and `final1` recovered; `final2` and fold0–fold7 missing |

This table separates verified results from recovery work. See [`../weights/README.md`](../weights/README.md) for the checksum inventory and [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) for release blockers.

## Evaluation definitions

The evaluator removes the first five seconds and reports `mir_eval` beat F-measure (±70 ms), CMLt, and AMLt. “All pieces” is a macro average over pieces, not a dataset-balanced average. The calibration procedure and its non-nested-selection limitation are documented in [`CALIBRATION.md`](CALIBRATION.md).
"""
    (ROOT / "docs/RESULTS.md").write_text(content, encoding="utf-8")


def write_validation_doc(rows: list[dict[str, object]], summary: dict) -> None:
    downbeat_count = len(finite_values(rows, "downbeat_fmeasure"))
    content = f"""# Result-table validation

Status: **PASS**

- Locked completion marker present.
- Candidate hash: `{CANDIDATE_HASH}`.
- Protocol hash: `{PROTOCOL_HASH}`.
- Default JSON parameters exactly match the locked selection and result summary.
- Coverage: {len(rows)} unique pieces, {len(DISPLAY_NAMES)} datasets, folds 0–7.
- Metric ranges: every finite value lies in [0, 1].
- Downbeat coverage: {downbeat_count} pieces; missing values occur only for Simac and SMC, consistently across all three downbeat metrics.
- Recomputed overall, SMC, and per-fold macro metrics match `summary.json` to absolute tolerance `1e-12`.
- Locked evaluation runtime recorded by the source bundle: {summary['elapsed_seconds']:.3f} seconds.

Run `python scripts/build_results_tables.py` from any directory to repeat validation and regenerate the public CSV/Markdown tables. This validator does not train a model or access a cluster.
"""
    (RESULTS / "VALIDATION.md").write_text(content, encoding="utf-8")


def main() -> None:
    rows = load_rows(LOCKED / "pieces.csv")
    summary = validate(rows)
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row["dataset"])].append(row)

    RESULTS.mkdir(exist_ok=True)
    write_dataset_csv(groups)
    folds = smc_fold_rows(rows)
    write_smc_csv(folds)
    write_results_doc(groups, folds)
    write_validation_doc(rows, summary)
    print(f"PASS: validated {len(rows)} pieces and rebuilt 4 result artifacts")


if __name__ == "__main__":
    main()
