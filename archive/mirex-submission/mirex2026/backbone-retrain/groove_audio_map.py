#!/usr/bin/env python3
"""Map the official Groove v1.0.0 WAVs to BeatThis's allowed split.

BeatThis flattens each source `drummer/session/take` path with underscores.
The source archive must first match the Magenta-published SHA-256 checksum.
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
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--wav-root", type=Path, required=True)
    parser.add_argument("--spectrogram-npz", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing map: {args.output}")
    import numpy as np
    import soundfile as sf

    wavs: dict[str, Path] = {}
    for path in args.wav_root.rglob("*.wav"):
        stem = "_".join(path.relative_to(args.wav_root).with_suffix("").parts)
        if stem in wavs:
            raise ValueError(f"ambiguous flattened Groove ID: {stem}")
        wavs[stem] = path
    if len(wavs) != 1090:
        raise ValueError(f"expected 1,090 Groove v1.0.0 WAVs, found {len(wavs)}")
    spectrograms = np.load(args.spectrogram_npz)
    split_path = args.annotations_root / "groove_midi" / "single.split"
    beats_root = args.annotations_root / "groove_midi" / "annotations" / "beats"
    rows: list[dict[str, str]] = []
    seen_hash: dict[str, tuple[str, str]] = {}
    duration_diffs: list[float] = []
    boundary_count = 0
    late_overhangs: list[tuple[float, str, str]] = []
    for line_no, line in enumerate(split_path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stem, split = line.split("\t")
        if split not in {"train", "val"}:
            raise ValueError(f"unexpected split at line {line_no}")
        path = wavs.get(stem)
        beats_path = beats_root / f"{stem}.beats"
        if path is None or not beats_path.is_file():
            raise FileNotFoundError(f"missing WAV/annotation for {stem}")
        duration = sf.info(str(path)).duration
        beat_times = [float(fields[0]) for text in beats_path.read_text().splitlines()
                      if (fields := text.split())]
        if not beat_times or min(beat_times) < -1 or sum(0 <= t <= duration for t in beat_times) < 2:
            raise ValueError(f"insufficient in-range beat labels for {stem}")
        if min(beat_times) < 0 or max(beat_times) > duration:
            boundary_count += 1
            late_overhangs.append((max(beat_times) - duration, stem, split))
        duration_diffs.append(abs(duration - spectrograms[f"{stem}/track"].shape[0] / 50))
        digest = hash_file(path)
        earlier = seen_hash.get(digest)
        if earlier is not None and earlier[1] != split:
            raise ValueError(f"cross-split exact WAV duplicate: {earlier} and {(stem, split)}")
        seen_hash.setdefault(digest, (stem, split))
        rows.append({"dataset": "groove_midi", "stem": stem, "audio_path": str(path.resolve())})
    if len(rows) != 336:
        raise ValueError(f"expected 336 BeatThis Groove pieces, got {len(rows)}")
    if max(duration_diffs) > 0.1:
        raise ValueError(f"Groove audio/cache duration mismatch: {max(duration_diffs):.3f}s")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("dataset", "stem", "audio_path"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"verified {len(rows)} Groove WAVs; max duration delta {max(duration_diffs):.3f}s; boundary clips {boundary_count}")
    print(f"late overhang >1s: {sum(seconds > 1 for seconds, _, _ in late_overhangs)}; >30s: {sum(seconds > 30 for seconds, _, _ in late_overhangs)}; validation: {sum(split == 'val' for _, _, split in late_overhangs)}")
    for seconds, stem, _ in sorted(late_overhangs, reverse=True)[:10]:
        print(f"late-label overhang requiring clip: {stem}: {seconds:.3f}s")


if __name__ == "__main__":
    main()
