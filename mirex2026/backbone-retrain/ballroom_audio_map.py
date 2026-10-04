#!/usr/bin/env python3
"""Match the original BallroomData WAVs to BeatThis's allowed split.

The Ballroom archive itself must first match the published MD5
2872a3e52070bc342a4510a95e2fa0b8. Never treat a basename-only match as
sufficient without the duration and cross-split duplicate checks below.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
from pathlib import Path
import wave


# Pairs documented by CPJKU/BallroomAnnotations, including acoustically similar
# recordings whose WAV bytes need not hash identically.
KNOWN_REPLICA_PAIRS = (
    ("Albums-AnaBelen_Veneo-11", "Albums-Chrisanne2-12"),
    ("Albums-Fire-08", "Albums-Fire-09"),
    ("Albums-Latin_Jam2-05", "Albums-Latin_Jam2-13"),
    ("Albums-Secret_Garden-01", "Media-104705"),
    ("Albums-AnaBelen_Veneo-03", "Albums-AnaBelen_Veneo-15"),
    ("Albums-Ballroom_Magic-03", "Albums-Ballroom_Magic-18"),
    ("Albums-Latin_Jam-04", "Albums-Latin_Jam-13"),
    ("Albums-Latin_Jam-08", "Albums-Latin_Jam-14"),
    ("Albums-Latin_Jam-06", "Albums-Latin_Jam-15"),
    ("Albums-Latin_Jam2-02", "Albums-Latin_Jam2-14"),
    ("Albums-Latin_Jam2-07", "Albums-Latin_Jam2-15"),
    ("Albums-Latin_Jam3-02", "Media-103414"),
    ("Media-103402", "Media-103415"),
)


def audio_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def map_audio(annotations_root: Path, audio_root: Path) -> tuple[list[dict[str, str]], list[str], list[str]]:
    split_file = annotations_root / "ballroom" / "single.split"
    beats_root = annotations_root / "ballroom" / "annotations" / "beats"
    wavs: dict[str, Path] = {}
    for wav in audio_root.rglob("*.wav"):
        if wav.name in wavs:
            raise ValueError(f"ambiguous Ballroom WAV basename: {wav.name}")
        wavs[wav.name] = wav
    if len(wavs) != 698:
        raise ValueError(f"expected 698 original Ballroom WAVs, found {len(wavs)}")
    rows: list[dict[str, str]] = []
    split_by_hash: dict[str, tuple[str, str]] = {}
    duplicate_notes: list[str] = []
    boundary_notes: list[str] = []
    split_by_stem: dict[str, str] = {}
    with split_file.open(encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            stem, split = line.rstrip("\n").split("\t")
            if not stem.startswith("ballroom_") or split not in {"train", "val"}:
                raise ValueError(f"malformed Ballroom split line {line_no}: {line!r}")
            split_by_stem[stem.removeprefix("ballroom_")] = split
            wav = wavs.get(stem.removeprefix("ballroom_") + ".wav")
            beat_file = beats_root / f"{stem}.beats"
            if wav is None or not beat_file.is_file():
                raise FileNotFoundError(f"missing Ballroom WAV/annotation for {stem}")
            with wave.open(str(wav), "rb") as sound:
                duration = sound.getnframes() / sound.getframerate()
            beat_times = [float(fields[0]) for line in beat_file.read_text().splitlines()
                          if (fields := line.split())]
            if not beat_times or min(beat_times) < -1.0 or max(beat_times) > duration + 1.0:
                raise ValueError(f"Ballroom beat labels outside WAV duration for {stem}: {duration}")
            if min(beat_times) < 0 or max(beat_times) > duration:
                boundary_notes.append(stem)
            content_hash = audio_hash(wav)
            earlier = split_by_hash.get(content_hash)
            if earlier is not None:
                duplicate_notes.append(f"{earlier[0]} ({earlier[1]}) == {stem} ({split})")
                if earlier[1] != split:
                    raise ValueError(f"cross-split duplicate Ballroom audio: {duplicate_notes[-1]}")
            else:
                split_by_hash[content_hash] = (stem, split)
            rows.append({"dataset": "ballroom", "stem": stem, "audio_path": str(wav.resolve())})
    if len(rows) != 685:
        raise ValueError(f"expected 685 BeatThis Ballroom pieces, mapped {len(rows)}")
    for first, second in KNOWN_REPLICA_PAIRS:
        first_split, second_split = split_by_stem.get(first), split_by_stem.get(second)
        if first_split is not None and second_split is not None and first_split != second_split:
            raise ValueError(f"known Ballroom recording replica crosses train/val: {first} ({first_split}) == {second} ({second_split})")
    return rows, duplicate_notes, boundary_notes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, duplicate_notes, boundary_notes = map_audio(args.annotations_root, args.audio_root)
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing map: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("dataset", "stem", "audio_path"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"mapped {len(rows)} Ballroom pieces; same-split exact WAV duplicates: {len(duplicate_notes)}; clips with a beat within one second outside WAV support: {len(boundary_notes)}")
    for note in duplicate_notes:
        print(note)
    for note in boundary_notes:
        print(f"boundary label clipped during training: {note}")


if __name__ == "__main__":
    main()
