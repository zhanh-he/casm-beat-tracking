#!/usr/bin/env python3
"""Index the public LabROSA Beatles MP3s as *unverified* BeatThis candidates.

The 2009 32 kbps mono recordings are not the BeatThis audio release. Album and
track-number matching only establishes identity, not annotation-time alignment
or suitability for training. Do not pass this index to beatfm_manifest.py.
"""

from __future__ import annotations

import argparse
import csv
from difflib import SequenceMatcher
from pathlib import Path
import re
import statistics


ALBUM_DIR = {
    "01": "Please_Please_Me", "02": "With_The_Beatles",
    "03": "A_Hard_Day_s_Night", "04": "Beatles_For_Sale",
    "05": "Help_", "06": "Rubber_Soul", "07": "Revolver",
    "08": "Sgt_Pepper_s_Lonely_Hearts_Club_Band",
    "09": "Magical_Mystery_Tour", "10_CD1": "The_White_Album_Disc_1",
    "10_CD2": "The_White_Album_Disc_2", "11": "Abbey_Road",
    "12": "Let_It_Be",
}


def normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def build_index(annotations_root: Path, mp3_root: Path) -> list[dict[str, str]]:
    import soundfile as sf

    wavs: dict[tuple[str, str], Path] = {}
    for album, directory in ALBUM_DIR.items():
        for path in (mp3_root / directory).glob("*.mp3"):
            match = re.match(r"^(\d{2})-(.*)\.mp3$", path.name)
            if match is None or (album, match[1]) in wavs:
                raise ValueError(f"ambiguous Beatles MP3: {path}")
            wavs[(album, match[1])] = path
    if len(wavs) != 180:
        raise ValueError(f"expected 180 LabROSA MP3s, found {len(wavs)}")
    rows: list[dict[str, str]] = []
    split_file = annotations_root / "beatles" / "single.split"
    for line_no, line in enumerate(split_file.read_text(encoding="utf-8-sig").splitlines(), 1):
        stem, split = line.split("\t")
        match = re.match(r"^beatles_(\d{2})(?:_(CD[12]))?_(.+)_(\d{2})_(.+)$", stem)
        if match is None or split not in {"train", "val"}:
            raise ValueError(f"malformed Beatles split line {line_no}: {line!r}")
        album = match[1] + ("_" + match[2] if match[2] else "")
        mp3 = wavs.get((album, match[4]))
        if mp3 is None:
            raise FileNotFoundError(f"no LabROSA recording by album/track number for {stem}")
        candidate_title = re.sub(r"^\d{2}-", "", mp3.stem)
        title_similarity = SequenceMatcher(
            None, normalized_title(match[5]), normalized_title(candidate_title),
        ).ratio()
        info = sf.info(str(mp3))
        rows.append({
            "stem": stem,
            "split": split,
            "source_album": ALBUM_DIR[album],
            "audio_path": str(mp3.resolve()),
            "audio_duration_seconds": f"{info.duration:.3f}",
            "title_similarity": f"{title_similarity:.3f}",
            "status": "identity_matched_time_alignment_unverified",
        })
    if len(rows) != 180 or {(r["source_album"], Path(r["audio_path"]).name) for r in rows} != {
        (ALBUM_DIR[a], p.name) for (a, _), p in wavs.items()
    }:
        raise ValueError("BeatThis/LabROSA Beatles title count mismatch")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--mp3-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing index: {args.output}")
    rows = build_index(args.annotations_root, args.mp3_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    scores = [float(row["title_similarity"]) for row in rows]
    print(f"identity-matched, alignment-unverified: {len(rows)} Beatles MP3s")
    print(f"title similarity min={min(scores):.3f}, median={statistics.median(scores):.3f}")
    for row in rows:
        if float(row["title_similarity"]) < 0.6:
            print(f"review title: {row['stem']} -> {Path(row['audio_path']).name}")


if __name__ == "__main__":
    main()
