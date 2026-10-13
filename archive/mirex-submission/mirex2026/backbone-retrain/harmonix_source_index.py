#!/usr/bin/env python3
"""Join Harmonix public source metadata to the BeatThis split, without audio.

This is only a provenance/availability index. YouTube versions are not the
original annotated recordings and require rights review plus time alignment
before they could be used as MERT training waveforms.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import statistics


def indexed_csv(path: Path, value_column: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"File", value_column} <= set(reader.fieldnames or ()):
            raise ValueError(f"unexpected Harmonix metadata columns: {path}")
        for row in reader:
            numeric_id = row["File"].split("_", 1)[0]
            if numeric_id in rows:
                raise ValueError(f"duplicate Harmonix numeric ID: {numeric_id}")
            rows[numeric_id] = row[value_column]
    return rows


def build_index(annotations_root: Path, harmonix_root: Path) -> list[dict[str, str]]:
    official = harmonix_root / "dataset"
    urls = indexed_csv(official / "youtube_urls.csv", "URL")
    scores = indexed_csv(official / "youtube_alignment_scores.csv", "score")
    official_labels: dict[str, Path] = {}
    for label in (official / "beats_and_downbeats").glob("*.txt"):
        numeric_id = label.stem.split("_", 1)[0]
        if numeric_id in official_labels:
            raise ValueError(f"duplicate official Harmonix numeric ID: {numeric_id}")
        official_labels[numeric_id] = label
    rows: list[dict[str, str]] = []
    split = annotations_root / "harmonix" / "single.split"
    for line_no, line in enumerate(split.read_text(encoding="utf-8-sig").splitlines(), 1):
        stem, part = line.split("\t")
        if part not in {"train", "val"}:
            raise ValueError(f"unexpected Harmonix split at line {line_no}")
        numeric_id = stem.split("_", 1)[0]
        official_label = official_labels.get(numeric_id)
        beatthis_label = annotations_root / "harmonix" / "annotations" / "beats" / f"{stem}.beats"
        if official_label is None or not official_label.is_file() or not beatthis_label.is_file():
            raise FileNotFoundError(f"missing official/BeatThis labels for {stem}")
        if numeric_id not in urls or numeric_id not in scores:
            raise ValueError(f"missing YouTube source metadata for {stem}")
        score = float(scores[numeric_id])
        if not 0 <= score <= 1:
            raise ValueError(f"invalid Harmonix alignment score for {stem}: {score}")
        rows.append({
            "stem": stem,
            "official_source_stem": official_label.stem,
            "split": part,
            "youtube_url": urls[numeric_id],
            "published_alignment_score": scores[numeric_id],
            "status": "metadata_only_no_verified_audio",
        })
    if len(rows) != 911:
        raise ValueError(f"expected 911 BeatThis Harmonix pieces, got {len(rows)}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--harmonix-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build_index(args.annotations_root, args.harmonix_root)
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing index: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    values = [float(row["published_alignment_score"]) for row in rows]
    print(f"metadata-only Harmonix index: {len(rows)} pieces, {sum(row['split']=='train' for row in rows)} train, {sum(row['split']=='val' for row in rows)} val")
    print(f"published alignment scores: min={min(values):.4f}, median={statistics.median(values):.4f}, below_0.9={sum(value < 0.9 for value in values)}")


if __name__ == "__main__":
    main()
