"""Freeze a BeatFM checkpoint using Direct beat metrics on allowed validation.

The selection rule is fixed before reading score files: maximize the
piece-macro average of 0.50*F + 0.25*CMLt + 0.25*AMLt on the 137 shared
Ballroom/RWC pieces. CASM and DBN rows are reported, never used to select.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import fmean


CANDIDATES = ("best_val_loss", "epoch_0005", "epoch_0010", "epoch_0015", "epoch_0020")
METHODS = ("direct", "casm_30_300", "dbn_55_215", "dbn_30_300")
METRICS = ("beat_f", "beat_cmlt", "beat_amlt", "downbeat_f",
           "downbeat_cmlt", "downbeat_amlt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite: {args.output}")
    if not (args.root / "COMPLETE").is_file():
        raise ValueError("BeatFM allowed-validation panel is not complete")
    provenance = json.loads((args.root / "provenance.json").read_text())
    if provenance.get("role") != "allowed-validation candidate screen; not MIREX test":
        raise ValueError("unexpected BeatFM evaluation role")
    if provenance.get("validation_pieces") != 137 or set(provenance.get("datasets", [])) != {"ballroom", "rwc"}:
        raise ValueError("checkpoint selection requires the exact common 137-piece panel")
    candidates = {record["name"]: record for record in provenance["checkpoint_candidates"]}
    if set(candidates) != set(CANDIDATES):
        raise ValueError("unexpected or missing BeatFM checkpoint candidates")
    with (args.root / "pieces.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    with (args.root / "summary.csv").open(newline="", encoding="utf-8") as handle:
        reported = list(csv.DictReader(handle))
    if len(rows) != len(CANDIDATES) * len(METHODS) * 137:
        raise ValueError("incomplete BeatFM score matrix")
    panel_ref: set[tuple[str, str]] | None = None
    decision_rows = []
    for name in CANDIDATES:
        digest = candidates[name]["sha256"]
        for method in METHODS:
            subset = [row for row in rows if row["candidate"] == name and row["method"] == method]
            panel = {(row["dataset"], row["stem"]) for row in subset}
            if len(subset) != 137 or len(panel) != 137 or {key[0] for key in panel} != {"ballroom", "rwc"}:
                raise ValueError(f"bad panel for {name}/{method}")
            if panel_ref is None:
                panel_ref = panel
            elif panel != panel_ref:
                raise ValueError(f"panel mismatch for {name}/{method}")
            if any(row["checkpoint_sha256"] != digest for row in subset):
                raise ValueError(f"checkpoint hash mismatch for {name}/{method}")
            computed = {}
            for metric in METRICS:
                values = [float(row[metric]) for row in subset]
                if not all(math.isfinite(value) for value in values):
                    raise ValueError(f"non-finite {metric} for {name}/{method}")
                computed[metric] = fmean(values)
            source = [row for row in reported if row["candidate"] == name
                      and row["method"] == method and row["dataset"] == "all"]
            if len(source) != 1 or int(source[0]["pieces"]) != 137:
                raise ValueError(f"missing source summary for {name}/{method}")
            for metric in METRICS:
                if abs(computed[metric] - float(source[0][metric])) > 1e-10:
                    raise ValueError(f"summary/piece mismatch: {name}/{method}/{metric}")
            decision_rows.append({"candidate": name, "method": method,
                                  "checkpoint_sha256": digest, "epoch": int(candidates[name]["epoch"]),
                                  "pieces": len(subset), **computed,
                                  "direct_beat_score": (0.5 * computed["beat_f"]
                                                        + 0.25 * computed["beat_cmlt"]
                                                        + 0.25 * computed["beat_amlt"])})
    direct_rows = [row for row in decision_rows if row["method"] == "direct"]
    chosen = max(direct_rows, key=lambda row: (row["direct_beat_score"], -row["epoch"]))
    payload = {
        "selection_status": "frozen using allowed validation only",
        "selection_rule": "maximize 0.50*beat_F + 0.25*beat_CMLt + 0.25*beat_AMLt on Direct",
        "selection_panel": "137 shared allowed-validation Ballroom/RWC pieces",
        "target_datasets_used": [],
        "selected_candidate": chosen["candidate"],
        "selected_checkpoint_sha256": chosen["checkpoint_sha256"],
        "selected_epoch": chosen["epoch"],
        "selected_score": chosen["direct_beat_score"],
        "pieces_csv_sha256": sha256((args.root / "pieces.csv").read_bytes()).hexdigest(),
        "provenance_sha256": sha256((args.root / "provenance.json").read_bytes()).hexdigest(),
        "panel_piece_count": len(panel_ref or ()),
        "scores": decision_rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(f"selected={chosen['candidate']} epoch={chosen['epoch']} score={chosen['direct_beat_score']:.6f}")


if __name__ == "__main__":
    main()
