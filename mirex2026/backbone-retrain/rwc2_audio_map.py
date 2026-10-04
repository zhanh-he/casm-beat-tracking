#!/usr/bin/env python3
"""Map verified RWC 2.0 WAVs to BeatThis's legacy RWC annotation stems.

Use only after verifying each downloaded ZIP against the Zenodo MD5. A map is
written only when every requested collection passes metadata, WAV-duration,
and beat-time checks. This does not make the other BeatFM datasets available.
"""

from __future__ import annotations

import argparse
from bisect import bisect_left
import csv
from dataclasses import dataclass
import math
from pathlib import Path
import re
import statistics
import sys
import wave


COLLECTIONS = {
    "popular": "P",
    "classical": "C",
    "jazz": "J",
    "royalty-free": "R",
}
STEM = re.compile(r"^rwc_(popular|classical|jazz|royalty-free)_CD(\d+)_(\d+)$")


def read_metadata(path: Path) -> dict[tuple[str, int, int], dict[str, str]]:
    result: dict[tuple[str, int, int], dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        required = {"RWCID", "CollID", "CDNo", "TrackNo", "duration"}
        if not required <= set(reader.fieldnames or ()):
            raise ValueError(f"RWC metadata is missing {required - set(reader.fieldnames or ())}")
        for row in reader:
            if row["CollID"] not in COLLECTIONS.values():
                continue
            key = (row["CollID"], int(row["CDNo"]), int(row["TrackNo"]))
            if key in result:
                raise ValueError(f"ambiguous RWC legacy CD/track key: {key}")
            result[key] = row
    return result


def read_beatthis(path: Path) -> list[tuple[float, int]]:
    events: list[tuple[float, int]] = []
    with path.open(encoding="utf-8-sig") as handle:
        for line in handle:
            fields = line.split()
            if fields:
                events.append((float(fields[0]), int(fields[1])))
    return events


def read_rwc2_beats(path: Path) -> list[tuple[float, int]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not {"t", "beat"} <= set(reader.fieldnames or ()):
            raise ValueError(f"unexpected RWC 2.0 beat CSV: {path}")
        return [(float(row["t"]), int(row["beat"])) for row in reader]


@dataclass(frozen=True)
class Alignment:
    shift_seconds: float  # add to BeatThis timestamps to align with RWC 2.0 WAV
    within_1ms: int
    within_100ms: int
    median_seconds: float
    p95_seconds: float
    meter_differences: int
    reference_density_difference: int


def alignment_stats(
    beatthis_events: list[tuple[float, int]], rwc2_events: list[tuple[float, int]],
    shift_seconds: float,
) -> Alignment:
    reference_times = [time for time, _ in rwc2_events]
    if not beatthis_events or not reference_times:
        raise ValueError("empty beat sequence")
    differences: list[float] = []
    meter_differences = 0
    for time, meter in beatthis_events:
        adjusted = time + shift_seconds
        location = bisect_left(reference_times, adjusted)
        candidates = [i for i in (location - 1, location) if 0 <= i < len(reference_times)]
        index = min(candidates, key=lambda i: abs(reference_times[i] - adjusted))
        difference = abs(reference_times[index] - adjusted)
        differences.append(difference)
        if difference <= .001:
            meter_differences += int(meter != rwc2_events[index][1])
    sorted_differences = sorted(differences)
    return Alignment(
        shift_seconds=shift_seconds,
        within_1ms=sum(d <= .001 for d in differences),
        within_100ms=sum(d <= .1 for d in differences),
        median_seconds=statistics.median(differences),
        p95_seconds=sorted_differences[round(.95 * (len(differences) - 1))],
        meter_differences=meter_differences,
        reference_density_difference=len(rwc2_events) - len(beatthis_events),
    )


def align_beat_times(
    beatthis_events: list[tuple[float, int]], rwc2_events: list[tuple[float, int]]
) -> Alignment:
    """Validate timing against RWC 2.0, allowing documented metrical edits.

    BeatThis uses half-time on many RWC Jazz tracks, and corrected individual
    beats in RWC Popular. A *constant* source-release offset is applied only
    when >=98% of beats then coincide within 1 ms; local corrections are
    retained without time warping. Larger disagreement rejects the recording.
    """
    baseline = alignment_stats(beatthis_events, rwc2_events, 0.0)
    candidate = round(rwc2_events[0][0] - beatthis_events[0][0], 3)
    chosen = baseline
    if 0 < abs(candidate) <= .5:
        shifted = alignment_stats(beatthis_events, rwc2_events, candidate)
        if shifted.within_1ms >= .98 * len(beatthis_events) and shifted.within_1ms > baseline.within_1ms + .5 * len(beatthis_events):
            chosen = shifted
    if not (
        chosen.within_1ms >= .98 * len(beatthis_events)
        or (chosen.median_seconds <= .03 and chosen.p95_seconds <= .07
            and chosen.within_100ms >= .98 * len(beatthis_events))
    ):
        raise ValueError(
            f"timing mismatch: {chosen.within_1ms}/{len(beatthis_events)} within 1ms, "
            f"median={chosen.median_seconds:.3f}s, p95={chosen.p95_seconds:.3f}s"
        )
    return chosen


def map_audio(
    annotations_root: Path,
    metadata_path: Path,
    rwc2_beats_root: Path,
    audio_root: Path,
    collections: set[str],
) -> list[dict[str, str]]:
    metadata = read_metadata(metadata_path)
    split = annotations_root / "rwc" / "single.split"
    beat_dir = annotations_root / "rwc" / "annotations" / "beats"
    rows: list[dict[str, str]] = []
    seen_audio: set[Path] = set()
    errors: list[str] = []
    meter_notes: list[str] = []
    density_notes: list[str] = []
    shift_notes: list[str] = []
    boundary_notes: list[str] = []
    correction_notes: list[str] = []
    with split.open(encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            stem = line.split("\t", 1)[0]
            match = STEM.fullmatch(stem)
            if match is None:
                errors.append(f"unrecognized BeatThis RWC stem: {stem}")
                continue
            subset, cd_no, track_no = match.groups()
            collection = COLLECTIONS[subset]
            if collection not in collections:
                continue
            key = (collection, int(cd_no), int(track_no))
            record = metadata.get(key)
            if record is None:
                errors.append(f"missing metadata for {stem}: {key}")
                continue
            rwc_id = record["RWCID"]
            wav = audio_root / f"RWC-{collection}" / f"{rwc_id}.wav"
            published_beats = rwc2_beats_root / f"RWC-{collection}" / f"{rwc_id}.csv"
            source_beats = beat_dir / f"{stem}.beats"
            if not wav.is_file() or not published_beats.is_file() or not source_beats.is_file():
                errors.append(f"missing WAV/beat labels for {stem}: {wav}")
                continue
            if wav in seen_audio:
                errors.append(f"multiple BeatThis stems map to {wav}")
                continue
            seen_audio.add(wav)
            with wave.open(str(wav), "rb") as sound:
                duration = sound.getnframes() / sound.getframerate()
            metadata_duration = float(record["duration"])
            if not math.isfinite(duration) or abs(duration - metadata_duration) > 0.01:
                errors.append(f"audio duration disagrees with RWC metadata for {stem}: {duration} vs {metadata_duration}")
                continue
            old_events = read_beatthis(source_beats)
            new_events = read_rwc2_beats(published_beats)
            try:
                alignment = align_beat_times(old_events, new_events)
            except ValueError as exc:
                errors.append(f"BeatThis/RWC 2.0 beat-time disagreement for {stem}: {exc}")
                continue
            if alignment.meter_differences:
                meter_notes.append(f"{stem}: {alignment.meter_differences} differing beat-in-bar labels")
            if alignment.reference_density_difference:
                density_notes.append(f"{stem}: {len(old_events)} BeatThis vs {len(new_events)} RWC 2.0 beats")
            if alignment.shift_seconds:
                shift_notes.append(f"{stem}: add {alignment.shift_seconds:+.3f}s to BeatThis labels")
            if alignment.within_1ms < .98 * len(old_events):
                correction_notes.append(
                    f"{stem}: {alignment.within_1ms}/{len(old_events)} exact beats; "
                    f"median={alignment.median_seconds:.3f}s p95={alignment.p95_seconds:.3f}s"
                )
            shifted_times = [time + alignment.shift_seconds for time, _ in old_events]
            if min(shifted_times) < -2.0 or max(shifted_times) > duration + 2.0:
                errors.append(f"BeatThis beat too far outside WAV duration for {stem}")
                continue
            outside_count = sum(time < 0 or time > duration for time in shifted_times)
            if outside_count:
                boundary_notes.append(f"{stem}: {outside_count} beats outside WAV support, to be clipped")
            rows.append({
                "dataset": "rwc", "stem": stem, "audio_path": str(wav.resolve()),
                "annotation_time_shift_seconds": f"{alignment.shift_seconds:.3f}",
            })
    if errors:
        raise ValueError(f"RWC mapping failed for {len(errors)} tracks: " + "; ".join(errors[:8]))
    if not rows:
        raise ValueError("no RWC tracks mapped")
    if meter_notes:
        print("RWC annotation meter-position differences (BeatThis labels retained): " + "; ".join(meter_notes), file=sys.stderr)
    if density_notes:
        print("RWC annotation beat-density differences (BeatThis labels retained): " + "; ".join(density_notes), file=sys.stderr)
    for label, notes in (("release offsets", shift_notes), ("local beat corrections", correction_notes),
                         ("boundary clips", boundary_notes)):
        if notes:
            print(f"RWC {label}: " + "; ".join(notes), file=sys.stderr)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--rwc-metadata", type=Path, required=True)
    parser.add_argument("--rwc2-beats-root", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--collections", nargs="+", choices=sorted(COLLECTIONS.values()), default=list(COLLECTIONS.values()))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = map_audio(
        args.annotations_root,
        args.rwc_metadata,
        args.rwc2_beats_root,
        args.audio_root,
        set(args.collections),
    )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing map: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("dataset", "stem", "audio_path", "annotation_time_shift_seconds"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"mapped {len(rows)} RWC tracks from {','.join(sorted(set(args.collections)))} to {args.output}")


if __name__ == "__main__":
    main()
