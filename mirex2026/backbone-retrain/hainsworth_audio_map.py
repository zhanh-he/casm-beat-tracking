#!/usr/bin/env python3
"""Verify the Hainsworth author-linked WAV mirror against BeatThis splits.

The WAVs are private research inputs, not repository assets. This emits only
paths and validation metadata, never copies audio into the repository.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
from pathlib import Path
import wave


def hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def map_audio(annotations_root: Path, wav_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    wavs = {path.stem: path for path in wav_root.glob("*.wav")}
    if len(wavs) != 222 or len(list(wav_root.glob("*.wav"))) != 222:
        raise ValueError(f"expected exactly 222 unique Hainsworth WAVs in {wav_root}")
    rows: list[dict[str, str]] = []
    boundary_notes: list[str] = []
    split_by_hash: dict[str, tuple[str, str]] = {}
    split_file = annotations_root / "hainsworth" / "single.split"
    beats_root = annotations_root / "hainsworth" / "annotations" / "beats"
    for line_no, line in enumerate(split_file.read_text(encoding="utf-8-sig").splitlines(), 1):
        stem, split = line.split("\t")
        if not stem.startswith("hainsworth_") or split not in {"train", "val"}:
            raise ValueError(f"malformed Hainsworth split line {line_no}: {line!r}")
        wav = wavs.get(stem.removeprefix("hainsworth_"))
        beat_file = beats_root / f"{stem}.beats"
        if wav is None or not beat_file.is_file():
            raise FileNotFoundError(f"missing Hainsworth WAV/annotation for {stem}")
        with wave.open(str(wav), "rb") as sound:
            if sound.getframerate() <= 0 or sound.getnchannels() < 1:
                raise ValueError(f"invalid WAV header: {wav}")
            duration = sound.getnframes() / sound.getframerate()
        beat_times = [float(fields[0]) for line in beat_file.read_text().splitlines()
                      if (fields := line.split())]
        if not beat_times or min(beat_times) < -1 or max(beat_times) > duration + 1:
            raise ValueError(f"beat labels beyond WAV support for {stem}: {duration:.3f}s")
        if min(beat_times) < 0 or max(beat_times) > duration:
            boundary_notes.append(stem)
        content_hash = hash_file(wav)
        earlier = split_by_hash.get(content_hash)
        if earlier is not None and earlier[1] != split:
            raise ValueError(f"cross-split exact WAV duplicate: {earlier} and {(stem, split)}")
        split_by_hash.setdefault(content_hash, (stem, split))
        rows.append({"dataset": "hainsworth", "stem": stem, "audio_path": str(wav.resolve())})
    if len(rows) != 222 or {row["stem"].removeprefix("hainsworth_") for row in rows} != set(wavs):
        raise ValueError("Hainsworth split/WAV identifiers do not match exactly")
    return rows, boundary_notes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--wav-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing map: {args.output}")
    rows, boundary_notes = map_audio(args.annotations_root, args.wav_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("dataset", "stem", "audio_path"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"mapped {len(rows)} Hainsworth WAVs; boundary-label clips: {len(boundary_notes)}")
    for stem in boundary_notes:
        print(f"boundary label to clip: {stem}")


if __name__ == "__main__":
    main()
