"""Score frozen BeatFM candidates on the permitted, piece-disjoint validation split.

SMC and GTZAN are rejected at manifest load. Each candidate uses the same
original WAVs, annotations, decoder defaults, and piece-macro metrics.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import numpy as np

from train_beatfm import Record, read_events, read_manifest


def checkpoint_argument(value: str) -> tuple[str, Path]:
    name, separator, path = value.partition("=")
    if not separator or not name or not path:
        raise argparse.ArgumentTypeError("checkpoint must be NAME=/absolute/path.pt")
    return name, Path(path)


def piece_scores(reference: np.ndarray, estimate: np.ndarray) -> dict[str, float]:
    import mir_eval

    if len(reference) < 2:
        return {"f": float("nan"), "cmlt": float("nan"), "amlt": float("nan")}
    # mir_eval expects both event series sorted and bounded to the audio.
    reference = np.sort(reference)
    estimate = np.sort(estimate)
    f = float(mir_eval.beat.f_measure(reference, estimate))
    cmlc, cmlt, amlc, amlt = mir_eval.beat.continuity(reference, estimate)
    return {"f": f, "cmlt": float(cmlt), "amlt": float(amlt)}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("no score rows")
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_relocated_validation(source_manifest: Path, relocated_manifest: Path,
                              *, subset: str = "verified-911") -> tuple[list[Record], str]:
    """Verify an off-cluster copy against the exact checkpoint split manifest."""
    source_hash = sha256(source_manifest.read_bytes()).hexdigest()
    with source_manifest.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    expected_total, expected_train = ((911, 774) if subset == "verified-911" else
                                      (1684, 1431) if subset == "expanded-1684" else (None, None))
    if expected_total is None or len(source_rows) != expected_total or sum(row["split"] == "train" for row in source_rows) != expected_train:
        raise ValueError(f"unexpected original {subset} split manifest")
    if len({(row["dataset"], row["stem"]) for row in source_rows}) != expected_total:
        raise ValueError("duplicate source-manifest piece")
    if any(row["dataset"].lower() in {"smc", "gtzan"} for row in source_rows):
        raise ValueError("forbidden source-manifest dataset")
    source_validation = {(row["dataset"], row["stem"]): row for row in source_rows
                         if row["split"] == "val" and row["dataset"] in {"ballroom", "rwc"}}
    if len(source_validation) != 137:
        raise ValueError("unexpected original validation count")
    with relocated_manifest.open(newline="", encoding="utf-8") as handle:
        relocated_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(relocated_rows) != 137:
        raise ValueError("incomplete relocated validation panel")
    base = relocated_manifest.parent.resolve()
    staged_provenance = json.loads((base / "provenance.json").read_text())
    staged_source_hash = staged_provenance.get("source_manifest_sha256")
    # The expanded manifest shares these exact 137 held-out pieces with the
    # audited 911 manifest; compare every non-path field below before reuse.
    expected_staged_hash = (source_hash if subset == "verified-911" else
                            "24deea630d5c7d8bf88f4f1d9c035c3370ae3a5ff181d448e5a164a9f5e13f1b")
    if staged_source_hash != expected_staged_hash or staged_provenance.get("validation_pieces") != 137:
        raise ValueError("staged panel provenance mismatch")
    records = []
    seen: set[tuple[str, str]] = set()
    for row in relocated_rows:
        key = (row["dataset"], row["stem"])
        if key in seen or key not in source_validation:
            raise ValueError(f"unknown or duplicate relocated piece: {key}")
        seen.add(key)
        original = source_validation[key]
        for field in ("dataset", "stem", "split", "annotation_time_shift_seconds", "beat_count", "downbeat_count"):
            if row[field] != original[field]:
                raise ValueError(f"relocated metadata mismatch: {key}/{field}")
        audio = (base / row["audio_path"]).resolve()
        annotation = (base / row["annotation_path"]).resolve()
        if not audio.is_relative_to(base) or not annotation.is_relative_to(base):
            raise ValueError(f"relocated path escapes staged panel: {key}")
        if not audio.is_file() or not annotation.is_file():
            raise FileNotFoundError(f"missing staged audio or annotation: {key}")
        records.append(Record(row["dataset"], row["stem"], row["split"], audio,
                              annotation, float(row["annotation_time_shift_seconds"]),
                              int(row["beat_count"]), int(row["downbeat_count"])))
    if seen != set(source_validation):
        raise ValueError("relocated validation panel omits source pieces")
    return records, source_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--checkpoint", type=checkpoint_argument, action="append", required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--mert-dir", type=Path, required=True)
    parser.add_argument("--casm-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--subset", choices=("verified-911", "expanded-1684"),
                        default="verified-911")
    parser.add_argument("--panel", choices=("all", "common-137"), default="all",
                        help="common-137 is the Ballroom/RWC panel shared by both subset recipes")
    parser.add_argument("--relocated-validation", type=Path,
                        help="private 137-piece off-cluster copy, validated against --manifest")
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error(f"refusing to overwrite: {args.output_dir}")
    if args.relocated_validation:
        if (args.subset, args.panel) not in {("verified-911", "all"), ("expanded-1684", "common-137")}:
            parser.error("relocation supports only the common Ballroom/RWC 137-piece panel")
        validation, manifest_hash = read_relocated_validation(
            args.manifest, args.relocated_validation, subset=args.subset)
    else:
        records, manifest_hash = read_manifest(
            args.manifest,
            verified_subset=args.subset == "verified-911",
            expanded_verified_subset=args.subset == "expanded-1684",
        )
        validation = [record for record in records if record.split == "val"]
    if args.panel == "common-137":
        validation = [record for record in validation if record.dataset in {"ballroom", "rwc"}]
    expected_count = 137 if args.subset == "verified-911" or args.panel == "common-137" else 253
    expected_datasets = ({"ballroom", "rwc"} if expected_count == 137 else
                         {"ballroom", "rwc", "hainsworth", "candombe", "groove_midi", "guitarset"})
    if len(validation) != expected_count or {record.dataset for record in validation} != expected_datasets:
        raise ValueError("unexpected validation inventory")
    if len({name for name, _ in args.checkpoint}) != len(args.checkpoint):
        raise ValueError("duplicate candidate names")

    import torch
    import soundfile as sf

    from mirex_pipeline.beatfm_backend import BeatFMBackend
    from mirex_pipeline.decoders import make_decoder

    # Verify every checkpoint before any scoring, including its training split.
    checkpoints = []
    for name, path in args.checkpoint:
        digest = sha256(path.read_bytes()).hexdigest()
        payload = torch.load(path, map_location="cpu", weights_only=True)
        recipe = payload.get("recipe") or {}
        if payload.get("manifest_sha256") != manifest_hash:
            raise ValueError(f"{name}: checkpoint/manifest mismatch")
        expected_recipe_key = ("verified_ballroom_rwc_subset" if args.subset == "verified-911"
                               else "expanded_verified_subset")
        if not recipe.get(expected_recipe_key) or recipe.get("pilot_partial_audio_not_submission"):
            raise ValueError(f"{name}: not an eligible {args.subset} candidate")
        checkpoints.append((name, path, digest, int(payload["epoch"]), payload.get("val_loss")))

    args.output_dir.mkdir(parents=True)
    provenance = {
        "role": "allowed-validation candidate screen; not MIREX test",
        "manifest": str(args.manifest),
        "manifest_sha256": manifest_hash,
        "subset": args.subset,
        "panel": args.panel,
        "relocated_validation": str(args.relocated_validation) if args.relocated_validation else None,
        "validation_pieces": len(validation),
        "datasets": sorted(expected_datasets),
        "checkpoint_candidates": [
            {"name": name, "path": str(path), "sha256": digest, "epoch": epoch, "val_loss": val_loss}
            for name, path, digest, epoch, val_loss in checkpoints
        ],
    }
    (args.output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    decoders = {
        "direct": make_decoder("direct", casm_config=args.casm_config, dbn_bpm=(55, 215)),
        "casm_30_300": make_decoder("casm", casm_config=args.casm_config, dbn_bpm=(55, 215)),
        "dbn_55_215": make_decoder("dbn", casm_config=args.casm_config, dbn_bpm=(55, 215)),
        "dbn_30_300": make_decoder("dbn", casm_config=args.casm_config, dbn_bpm=(30, 300)),
    }
    rows: list[dict[str, object]] = []
    started = time.monotonic()
    for name, path, digest, epoch, val_loss in checkpoints:
        backend = BeatFMBackend(checkpoint=path, device=args.device)
        candidate_rows: list[dict[str, object]] = []
        for index, record in enumerate(validation, 1):
            info = sf.info(str(record.audio_path))
            duration = info.frames / info.samplerate
            beat_ref, downbeat_ref = read_events(record.annotation_path)
            shift = record.annotation_time_shift_seconds
            beat_ref = np.asarray([t + shift for t in beat_ref if 0 <= t + shift < duration], dtype=np.float64)
            downbeat_ref = np.asarray([t + shift for t in downbeat_ref if 0 <= t + shift < duration], dtype=np.float64)
            activations = backend.predict(record.audio_path)
            for method, decoder in decoders.items():
                beat, downbeat = decoder.decode(activations)
                beat = np.asarray(beat, dtype=np.float64)
                downbeat = np.asarray(downbeat, dtype=np.float64)
                if not np.all(np.isfinite(beat)) or np.any(np.diff(beat) <= 0):
                    raise ValueError(f"invalid beat output: {name}/{method}/{record.stem}")
                beat_metrics = piece_scores(beat_ref, beat)
                downbeat_metrics = piece_scores(downbeat_ref, downbeat)
                candidate_rows.append({
                    "candidate": name, "checkpoint_sha256": digest, "epoch": epoch,
                    "val_loss": val_loss, "dataset": record.dataset, "stem": record.stem,
                    "method": method, "beat_f": beat_metrics["f"],
                    "beat_cmlt": beat_metrics["cmlt"], "beat_amlt": beat_metrics["amlt"],
                    "downbeat_f": downbeat_metrics["f"],
                    "downbeat_cmlt": downbeat_metrics["cmlt"],
                    "downbeat_amlt": downbeat_metrics["amlt"],
                    "beat_ref_count": len(beat_ref), "downbeat_ref_count": len(downbeat_ref),
                    "beat_pred_count": len(beat), "downbeat_pred_count": len(downbeat),
                })
            if index % 10 == 0 or index == len(validation):
                print(json.dumps({"candidate": name, "done": index, "total": len(validation),
                                  "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
        write_csv(args.output_dir / f"candidate_{name}.csv", candidate_rows)
        rows.extend(candidate_rows)
        del backend
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    write_csv(args.output_dir / "pieces.csv", rows)
    summary = []
    for name, _, digest, epoch, val_loss in checkpoints:
        for method in decoders:
            for dataset in ("all", *sorted(expected_datasets)):
                subset = [row for row in rows if row["candidate"] == name and row["method"] == method
                          and (dataset == "all" or row["dataset"] == dataset)]
                item: dict[str, object] = {"candidate": name, "checkpoint_sha256": digest,
                                           "epoch": epoch, "val_loss": val_loss,
                                           "method": method, "dataset": dataset, "pieces": len(subset)}
                for metric in ("beat_f", "beat_cmlt", "beat_amlt", "downbeat_f", "downbeat_cmlt", "downbeat_amlt"):
                    values = np.asarray([row[metric] for row in subset], dtype=np.float64)
                    item[metric] = float(np.nanmean(values)) if np.any(np.isfinite(values)) else float("nan")
                summary.append(item)
    write_csv(args.output_dir / "summary.csv", summary)
    (args.output_dir / "COMPLETE").write_text("allowed validation complete\n")


if __name__ == "__main__":
    main()
