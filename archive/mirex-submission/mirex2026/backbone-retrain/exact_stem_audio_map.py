#!/usr/bin/env python3
"""Verify an exact-stem source audio collection against BeatThis labels/cache.

For Candombe and GuitarSet only: source basenames must equal split stems.
Checks IDs, duration, label bounds, and cross-split exact audio duplicates.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
from pathlib import Path


def hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("candombe", "guitarset"), required=True)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--spectrogram-npz", type=Path, required=True)
    parser.add_argument("--suffix", choices=(".flac", ".wav"), required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--expected-source-count", type=int,
                        help="source may contain more recordings than the BeatThis split")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing map: {args.output}")
    import numpy as np
    import soundfile as sf

    audio = {path.stem: path for path in args.audio_root.rglob(f"*{args.suffix}")}
    source_count = args.expected_source_count or args.expected_count
    if len(audio) != source_count:
        raise ValueError(f"expected {source_count} unique source recordings, found {len(audio)}")
    spectrograms = np.load(args.spectrogram_npz)
    split_path = args.annotations_root / args.dataset / "single.split"
    beats_root = args.annotations_root / args.dataset / "annotations" / "beats"
    rows: list[dict[str, str]] = []
    seen_hash: dict[str, tuple[str, str]] = {}
    duration_diffs: list[float] = []
    boundary_count = 0
    for line_no, line in enumerate(split_path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stem, split = line.split("\t")
        if split not in {"train", "val"}:
            raise ValueError(f"unexpected split at line {line_no}")
        path = audio.get(stem)
        beats_path = beats_root / f"{stem}.beats"
        if path is None or not beats_path.is_file():
            raise FileNotFoundError(f"missing audio/annotation for {stem}")
        duration = sf.info(str(path)).duration
        beat_times = [float(fields[0]) for text in beats_path.read_text().splitlines()
                      if (fields := text.split())]
        if not beat_times or min(beat_times) < -1 or max(beat_times) > duration + 1:
            raise ValueError(f"beats beyond audio support for {stem}")
        boundary_count += int(min(beat_times) < 0 or max(beat_times) > duration)
        frames = spectrograms[f"{stem}/track"].shape[0]
        duration_diffs.append(abs(duration - frames / 50))
        digest = hash_file(path)
        earlier = seen_hash.get(digest)
        if earlier is not None and earlier[1] != split:
            raise ValueError(f"exact cross-split duplicate: {earlier} and {(stem, split)}")
        seen_hash.setdefault(digest, (stem, split))
        rows.append({"dataset": args.dataset, "stem": stem, "audio_path": str(path.resolve())})
    if len(rows) != args.expected_count or len({r["stem"] for r in rows}) != args.expected_count:
        raise ValueError("split count or uniqueness differs from expected")
    if source_count == args.expected_count and {r["stem"] for r in rows} != set(audio):
        raise ValueError("split and source audio IDs differ")
    if max(duration_diffs) > 0.1:
        raise ValueError(f"audio differs from released BeatThis spectrogram duration by {max(duration_diffs):.3f}s")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("dataset", "stem", "audio_path"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"verified {len(rows)} {args.dataset} recordings; max duration delta {max(duration_diffs):.3f}s; boundary clips {boundary_count}")


if __name__ == "__main__":
    main()
