"""Audit the shared 137-piece Ballroom/RWC validation panel across backbones.

BeatThis here is its held-out search checkpoint, not the final all-allowed
retrain. MSCNN and BeatFM use their declared train-split checkpoints. The
table is development evidence only, never an official MIREX test result.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import fmean


METHODS = (
    ("direct", "direct"),
    ("casm_no_smc", "casm_30_300"),
    ("dbn_55_215", "dbn_55_215"),
    ("dbn_30_300", "dbn_30_300"),
)
METRICS = ("beat_f", "beat_cmlt", "beat_amlt", "downbeat_f", "downbeat_cmlt", "downbeat_amlt")
BEATTHIS_SHA = "cd8a8c93b11c189daab497076261730bc8a059fa2b8d2b9c07b012c2d9c4bd4d"
MSCNN_SHA = "6cb647407caf367e1e3e66d13061a4459899f26e1ae0001e5c519cac95ab30b1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def baseline_rows(path: Path) -> dict[tuple[str, str], dict[str, float]]:
    rows = read_csv(path)
    panel: dict[tuple[str, str], dict[str, float]] = {}
    for row in rows:
        dataset = row["dataset"]
        if dataset == "ballroom":
            group = "ballroom"
        elif dataset.startswith("rwc_"):
            group = "rwc"
        else:
            continue
        parts = Path(row["piece"]).parts
        if len(parts) < 3:
            raise ValueError(f"unexpected baseline piece key: {row['piece']}")
        key = (group, parts[1])
        if key in panel:
            raise ValueError(f"duplicate baseline piece: {key}")
        panel[key] = {
            "beat_f": float(row["beat_fmeasure"]), "beat_cmlt": float(row["beat_cmlt"]),
            "beat_amlt": float(row["beat_amlt"]),
            "downbeat_f": float(row["downbeat_fmeasure"]),
            "downbeat_cmlt": float(row["downbeat_cmlt"]),
            "downbeat_amlt": float(row["downbeat_amlt"]),
        }
    return panel


def beatfm_rows(rows: list[dict[str, str]], candidate: str, method: str) -> dict[tuple[str, str], dict[str, float]]:
    panel: dict[tuple[str, str], dict[str, float]] = {}
    for row in rows:
        if row["candidate"] != candidate or row["method"] != method:
            continue
        key = (row["dataset"], row["stem"])
        if key in panel:
            raise ValueError(f"duplicate BeatFM piece: {key}")
        panel[key] = {metric: float(row[metric]) for metric in METRICS}
    return panel


def validate_panel(panel: dict[tuple[str, str], dict[str, float]]) -> None:
    if len(panel) != 137 or sum(group == "ballroom" for group, _ in panel) != 103 or sum(group == "rwc" for group, _ in panel) != 34:
        raise ValueError("unexpected common-panel size or dataset mix")
    for values in panel.values():
        if any(not math.isfinite(values[metric]) for metric in METRICS):
            raise ValueError("non-finite common-panel metric")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beatthis-dir", type=Path, required=True)
    parser.add_argument("--mscnn-dir", type=Path, required=True)
    parser.add_argument("--beatfm-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error(f"refusing to overwrite: {args.output_dir}")
    selection = json.loads((args.beatfm_dir / "selection.json").read_text())
    if selection.get("target_datasets_used") != [] or selection.get("panel_piece_count") != 137:
        raise ValueError("BeatFM choice was not frozen on the common allowed panel")
    candidate = selection["selected_candidate"]
    beatfm_source = args.beatfm_dir / "pieces.csv"
    fm_all = read_csv(beatfm_source)
    summary = []
    source_hashes = {str(beatfm_source): sha256(beatfm_source.read_bytes()).hexdigest()}
    reference_keys: set[tuple[str, str]] | None = None
    for display_method, fm_method in METHODS:
        sources = (
            ("beatthis_search", args.beatthis_dir / f"{display_method}.pieces.csv", BEATTHIS_SHA),
            ("mscnn_split", args.mscnn_dir / f"{display_method}.pieces.csv", MSCNN_SHA),
        )
        panels = []
        for model, path, digest in sources:
            panel = baseline_rows(path)
            source_hashes[str(path)] = sha256(path.read_bytes()).hexdigest()
            panels.append((model, panel, digest))
        panels.append(("beatfm_911_split", beatfm_rows(fm_all, candidate, fm_method),
                       selection["selected_checkpoint_sha256"]))
        for model, panel, digest in panels:
            validate_panel(panel)
            if reference_keys is None:
                reference_keys = set(panel)
            elif set(panel) != reference_keys:
                raise ValueError(f"cross-backbone piece identity mismatch: {model}/{display_method}")
            for dataset in ("all", "ballroom", "rwc"):
                keys = [key for key in panel if dataset == "all" or key[0] == dataset]
                scores = {metric: fmean(panel[key][metric] for key in keys) for metric in METRICS}
                summary.append({"backbone": model, "checkpoint_sha256": digest,
                                "method": display_method, "dataset": dataset,
                                "pieces": len(keys), **scores})
    args.output_dir.mkdir(parents=True)
    with (args.output_dir / "summary.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    (args.output_dir / "provenance.json").write_text(json.dumps({
        "role": "exact common allowed-validation comparison, not MIREX test",
        "models": ["beatthis_search", "mscnn_split", "beatfm_911_split"],
        "selected_beatfm_candidate": candidate,
        "validation_pieces": len(reference_keys or ()),
        "source_csv_sha256": source_hashes,
        "target_datasets_used": [],
    }, indent=2) + "\n")
    print(f"wrote {len(summary)} rows on {len(reference_keys or ())} identical allowed pieces")


if __name__ == "__main__":
    main()
