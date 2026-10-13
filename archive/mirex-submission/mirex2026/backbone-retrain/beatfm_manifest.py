"""Build a disjoint BeatFM manifest from BeatThis's official single splits.

This is intentionally a strict preflight: a training manifest is not written
unless *every* usable allowed song has a corresponding original audio file.
An explicitly labeled partial-audio manifest is available for smoke/pilot
experiments. Separately declared 911-piece and 1,684-piece original-audio
subsets are allowed for MIREX candidates, but never mislabeled as the full
BeatThis pool.
BeatThis spectrogram caches are not valid MERT inputs.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
import sys


AUDIO_SUFFIXES = (".wav", ".flac", ".mp3", ".ogg", ".m4a")
HELD_OUT = frozenset({"smc", "gtzan"})


@dataclass(frozen=True)
class Piece:
    dataset: str
    stem: str
    split: str
    annotation: Path
    beat_count: int
    downbeat_count: int


@dataclass(frozen=True)
class AudioRef:
    path: Path
    annotation_time_shift_seconds: float = 0.0


def annotation_counts(path: Path) -> tuple[int, int]:
    beats = downbeats = 0
    with path.open(encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            fields = line.split()
            if not fields:
                continue
            try:
                timestamp = float(fields[0])
            except ValueError as exc:
                raise ValueError(f"{path}:{line_no}: invalid beat time") from exc
            # Some Harmonix annotations include a beat just before time zero.
            # Keep the piece; the waveform-aligned target builder must clip it.
            if not math.isfinite(timestamp):
                raise ValueError(f"{path}:{line_no}: non-finite beat time")
            beats += 1
            if len(fields) > 1:
                try:
                    downbeats += int(float(fields[1]) == 1)
                except ValueError as exc:
                    raise ValueError(f"{path}:{line_no}: invalid beat position") from exc
    return beats, downbeats


def load_allowed_splits(annotations_root: Path) -> tuple[list[Piece], list[str]]:
    pieces: list[Piece] = []
    skipped: list[str] = []
    seen: set[tuple[str, str]] = set()
    splits = sorted(annotations_root.glob("*/single.split"))
    if not splits:
        raise FileNotFoundError(f"no single.split files under {annotations_root}")
    for split_file in splits:
        dataset = split_file.parent.name
        if dataset in HELD_OUT:
            continue
        with split_file.open(encoding="utf-8-sig") as handle:
            for line_no, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                fields = line.rstrip("\n").split("\t")
                if len(fields) != 2 or fields[1] not in {"train", "val"}:
                    raise ValueError(f"{split_file}:{line_no}: expected stem<TAB>train|val")
                stem, split = fields
                key = (dataset, stem)
                if not stem or key in seen:
                    raise ValueError(f"{split_file}:{line_no}: duplicate or empty stem")
                seen.add(key)
                annotation = split_file.parent / "annotations" / "beats" / f"{stem}.beats"
                if not annotation.is_file():
                    skipped.append(f"{dataset}/{stem}: missing beat annotation")
                    continue
                beat_count, downbeat_count = annotation_counts(annotation)
                if beat_count == 0:
                    skipped.append(f"{dataset}/{stem}: empty beat annotation")
                    continue
                pieces.append(Piece(dataset, stem, split, annotation, beat_count, downbeat_count))
    if not pieces:
        raise ValueError("no usable allowed training or validation pieces")
    if not any(p.split == "train" for p in pieces) or not any(p.split == "val" for p in pieces):
        raise ValueError("both train and validation pieces are required")
    return pieces, skipped


def load_audio_map(path: Path) -> dict[tuple[str, str], AudioRef]:
    mapping: dict[tuple[str, str], AudioRef] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not {"dataset", "stem", "audio_path"} <= set(reader.fieldnames):
            raise ValueError("audio map must have dataset, stem, audio_path TSV columns")
        for row in reader:
            key = (row["dataset"], row["stem"])
            if key in mapping:
                raise ValueError(f"duplicate audio mapping for {key}")
            shift = float(row.get("annotation_time_shift_seconds") or 0.0)
            if not math.isfinite(shift) or abs(shift) > 0.5:
                raise ValueError(f"invalid RWC audio-release annotation shift for {key}: {shift}")
            mapping[key] = AudioRef(Path(row["audio_path"]).expanduser().resolve(), shift)
    return mapping


def find_audio(piece: Piece, audio_root: Path | None, audio_map: dict[tuple[str, str], AudioRef]) -> AudioRef | None:
    mapped = audio_map.get((piece.dataset, piece.stem))
    if mapped is not None:
        return mapped if mapped.path.is_file() else None
    if audio_root is None:
        return None
    candidates = [audio_root / piece.dataset / f"{piece.stem}{suffix}" for suffix in AUDIO_SUFFIXES]
    existing = [path.resolve() for path in candidates if path.is_file()]
    if len(existing) > 1:
        raise ValueError(f"ambiguous audio for {piece.dataset}/{piece.stem}: {existing}")
    return AudioRef(existing[0]) if existing else None


def build_manifest(
    annotations_root: Path,
    *,
    audio_root: Path | None = None,
    audio_map_path: Path | None = None,
    extra_audio_maps: list[Path] | None = None,
    pilot_partial_audio: bool = False,
    verified_subset: bool = False,
    expanded_verified_subset: bool = False,
    output: Path | None = None,
) -> dict[str, object]:
    if sum((pilot_partial_audio, verified_subset, expanded_verified_subset)) > 1:
        raise ValueError("pilot and verified-subset modes are mutually exclusive")
    pieces, skipped = load_allowed_splits(annotations_root)
    audio_map = load_audio_map(audio_map_path) if audio_map_path else {}
    for additional_map in extra_audio_maps or []:
        extra = load_audio_map(additional_map)
        overlap = set(audio_map) & set(extra)
        if overlap:
            raise ValueError(f"duplicate piece across audio maps: {sorted(overlap)[:5]}")
        audio_map.update(extra)
    rows: list[dict[str, str | int]] = []
    missing_audio: list[str] = []
    counts: dict[str, dict[str, int]] = {}
    for piece in pieces:
        counts.setdefault(piece.dataset, {"train": 0, "val": 0})[piece.split] += 1
        audio_ref = find_audio(piece, audio_root, audio_map)
        if audio_ref is None:
            missing_audio.append(f"{piece.dataset}/{piece.stem}")
            continue
        rows.append({
            "dataset": piece.dataset,
            "stem": piece.stem,
            "split": piece.split,
            "audio_path": str(audio_ref.path),
            "annotation_path": str(piece.annotation.resolve()),
            "annotation_time_shift_seconds": f"{audio_ref.annotation_time_shift_seconds:.3f}",
            "beat_count": piece.beat_count,
            "downbeat_count": piece.downbeat_count,
        })
    digest = sha256()
    for piece in pieces:
        digest.update(f"{piece.dataset}\t{piece.stem}\t{piece.split}\n".encode())
        digest.update(piece.annotation.read_bytes())
    summary: dict[str, object] = {
        "protocol": "BeatThis single.split; supervised no-SMC and GTZAN-held-out",
        "source_zip_sha256": "4fbf554a78f2f353d1461f2267fa45f43b6cf864fc423f146ae46d301018858a",
        "allowed_train_pieces": sum(p.split == "train" for p in pieces),
        "allowed_val_pieces": sum(p.split == "val" for p in pieces),
        "per_dataset": counts,
        "skipped_annotations": skipped,
        "missing_audio_count": len(missing_audio),
        "missing_audio_examples": missing_audio[:20],
        "manifest_role": (
            "pilot_partial_audio_not_submission" if pilot_partial_audio else
            "verified_ballroom_rwc_subset_candidate" if verified_subset else
            "expanded_verified_1684_subset_candidate" if expanded_verified_subset else
            "complete_allowed_pool"
        ),
        "mapped_train_pieces": sum(row["split"] == "train" for row in rows),
        "mapped_val_pieces": sum(row["split"] == "val" for row in rows),
        "mapped_shifted_annotation_pieces": sum(float(row["annotation_time_shift_seconds"]) != 0 for row in rows),
        "split_and_annotation_sha256": digest.hexdigest(),
    }
    if output is not None:
        if audio_root is None and audio_map_path is None and not extra_audio_maps:
            raise ValueError("--output requires --audio-root or --audio-map")
        if verified_subset:
            selected = {(str(row["dataset"]), str(row["stem"])) for row in rows}
            by_dataset_split = {
                (dataset, split): sum(row["dataset"] == dataset and row["split"] == split for row in rows)
                for dataset in ("ballroom", "rwc") for split in ("train", "val")
            }
            if (by_dataset_split != {
                ("ballroom", "train"): 582, ("ballroom", "val"): 103,
                ("rwc", "train"): 192, ("rwc", "val"): 34,
            } or len(selected) != 911 or len(rows) != 911):
                raise ValueError(
                    "verified subset requires Ballroom 582/103 and RWC 192/34 train/val pieces"
                )
        if expanded_verified_subset:
            expected = {
                ("ballroom", "train"): 582, ("ballroom", "val"): 103,
                ("rwc", "train"): 192, ("rwc", "val"): 34,
                ("hainsworth", "train"): 189, ("hainsworth", "val"): 33,
                ("candombe", "train"): 30, ("candombe", "val"): 5,
                ("groove_midi", "train"): 285, ("groove_midi", "val"): 51,
                ("guitarset", "train"): 153, ("guitarset", "val"): 27,
            }
            actual = {
                key: sum((row["dataset"], row["split"]) == key for row in rows)
                for key in expected
            }
            if len(rows) != 1684 or actual != expected:
                raise ValueError("expanded verified subset requires audited 1,431/253 pieces by dataset")
        if missing_audio and not (pilot_partial_audio or verified_subset or expanded_verified_subset):
            raise ValueError(
                f"refusing incomplete training manifest: {len(missing_audio)} original audio files missing; "
                f"examples: {missing_audio[:5]}"
            )
        if not rows or not any(row["split"] == "train" for row in rows) or not any(row["split"] == "val" for row in rows):
            raise ValueError("output manifest requires mapped train and validation audio")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(output)
        summary["manifest_path"] = str(output.resolve())
        summary["manifest_sha256"] = sha256(output.read_bytes()).hexdigest()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path)
    parser.add_argument("--audio-map", type=Path, action="append")
    parser.add_argument("--pilot-partial-audio", action="store_true", help="write only mapped songs; never a submission manifest")
    parser.add_argument("--verified-subset", action="store_true", help="explicit 911-piece Ballroom/RWC candidate; not the full-data comparison")
    parser.add_argument("--expanded-verified-subset", action="store_true",
                        help="explicit audited 1,684-piece original-audio candidate; not full-data reproduction")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        summary = build_manifest(
            args.annotations_root,
            audio_root=args.audio_root,
            audio_map_path=args.audio_map[0] if args.audio_map else None,
            extra_audio_maps=args.audio_map[1:] if args.audio_map else None,
            pilot_partial_audio=args.pilot_partial_audio,
            verified_subset=args.verified_subset,
            expanded_verified_subset=args.expanded_verified_subset,
            output=args.output,
        )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"BeatFM manifest preflight failed: {exc}\n")
    json.dump(summary, sys.stdout, indent=2, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
