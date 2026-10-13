"""Audit four MSCNN candidates and freeze a choice using allowed Beatles only."""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import fmean


CANDIDATES = ("best_0119", "best_0139", "best_0154", "last_1499")
METHODS = ("direct", "casm_no_smc", "dbn_55_215", "dbn_30_300")
METRICS = ("beat_fmeasure", "beat_cmlt", "beat_amlt",
           "downbeat_fmeasure", "downbeat_cmlt", "downbeat_amlt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite: {args.output}")
    panel_ref: set[tuple[str, str]] | None = None
    summary_rows = []
    for candidate in CANDIDATES:
        for method in METHODS:
            path = args.root / candidate / f"{method}.pieces.csv"
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            panel = {(row["piece"], row["dataset"]) for row in rows}
            if len(rows) != 556 or len(panel) != 556:
                raise ValueError(f"expected 556 unique allowed-validation pieces: {path}")
            if any(dataset.lower() in {"smc", "gtzan"} for _, dataset in panel):
                raise ValueError(f"forbidden dataset in allowed-validation panel: {path}")
            if panel_ref is None:
                panel_ref = panel
            elif panel != panel_ref:
                raise ValueError(f"candidate/decoder panel mismatch: {path}")
            for row in rows:
                for metric in METRICS:
                    value = float(row[metric])
                    if not math.isfinite(value):
                        raise ValueError(f"non-finite {metric} in {path}: {row['piece']}")
            reported = json.loads((args.root / candidate / f"{method}.summary.json").read_text())
            for dataset in ("all", "beatles", "ballroom", "rwc"):
                subset = (rows if dataset == "all" else
                          [row for row in rows if row["dataset"].startswith("rwc_")] if dataset == "rwc" else
                          [row for row in rows if row["dataset"] == dataset])
                if not subset:
                    raise ValueError(f"missing {dataset} in {path}")
                if dataset == "beatles" and len(subset) != 27:
                    raise ValueError(f"expected 27 Beatles validation pieces in {path}")
                computed = {metric: fmean(float(row[metric]) for row in subset) for metric in METRICS}
                if dataset != "rwc":
                    source = reported["macro_piece"] if dataset == "all" else reported["per_dataset"][dataset]
                    for metric, value in computed.items():
                        if abs(value - float(source[metric])) > 1e-10:
                            raise ValueError(f"summary/piece mismatch for {candidate}/{method}/{dataset}/{metric}")
                clean_score = (
                    0.6 * (0.5 * computed["beat_fmeasure"] + 0.25 * computed["beat_cmlt"]
                           + 0.25 * computed["beat_amlt"])
                    + 0.4 * (0.5 * computed["downbeat_fmeasure"] + 0.25 * computed["downbeat_cmlt"]
                             + 0.25 * computed["downbeat_amlt"])
                )
                summary_rows.append({"candidate": candidate, "method": method, "dataset": dataset,
                                     "pieces": len(subset), **computed, "clean_score": clean_score,
                                     "pieces_sha256": sha256(path.read_bytes()).hexdigest()})
    direct_beatles = [row for row in summary_rows if row["method"] == "direct" and row["dataset"] == "beatles"]
    chosen = max(direct_beatles, key=lambda row: (row["clean_score"], row["candidate"]))
    payload = {
        "selection_status": "frozen from allowed validation only",
        "selected_candidate": chosen["candidate"],
        "selected_direct_beatles_score": chosen["clean_score"],
        "selection_formula": "0.60*beat(0.50*F+0.25*CMLt+0.25*AMLt)+0.40*downbeat(0.50*F+0.25*CMLt+0.25*AMLt)",
        "selection_decoder": "direct",
        "selection_dataset": "27 allowed-validation Beatles pieces",
        "candidate_count": len(CANDIDATES),
        "allowed_validation_pieces": len(panel_ref or ()),
        "target_datasets_used": [],
        "summary": summary_rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(f"selected={chosen['candidate']} score={chosen['clean_score']:.6f} panel={len(panel_ref or ())}")


if __name__ == "__main__":
    main()
