#!/usr/bin/env python3
"""Quantify timing differences between BeatThis and RWC 2.0 beat labels."""

from __future__ import annotations

import argparse
from bisect import bisect_left
from pathlib import Path
import statistics
import wave

from rwc2_audio_map import COLLECTIONS, STEM, read_beatthis, read_metadata, read_rwc2_beats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--rwc-metadata", type=Path, required=True)
    parser.add_argument("--rwc2-beats-root", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--collection", choices=sorted(COLLECTIONS.values()), required=True)
    args = parser.parse_args()
    metadata = read_metadata(args.rwc_metadata)
    print("stem\tbeatthis_n\trwc2_n\twithin_1ms\twithin_50ms\twithin_100ms\tmedian_nearest_ms\tp95_nearest_ms\tbeatthis_beyond_wav_n\twav_duration_s")
    for line in (args.annotations_root / "rwc" / "single.split").read_text().splitlines():
        stem = line.split("\t", 1)[0]
        match = STEM.fullmatch(stem)
        if match is None:
            continue
        subset, cd_no, track_no = match.groups()
        collection = COLLECTIONS[subset]
        if collection != args.collection:
            continue
        record = metadata[(collection, int(cd_no), int(track_no))]
        rwc_id = record["RWCID"]
        old = read_beatthis(args.annotations_root / "rwc" / "annotations" / "beats" / f"{stem}.beats")
        new = read_rwc2_beats(args.rwc2_beats_root / f"RWC-{collection}" / f"{rwc_id}.csv")
        new_times = [time for time, _ in new]
        differences = []
        for time, _ in old:
            index = bisect_left(new_times, time)
            differences.append(min(abs(new_times[i] - time) for i in (index - 1, index) if 0 <= i < len(new_times)))
        wav = args.audio_root / f"RWC-{collection}" / f"{rwc_id}.wav"
        with wave.open(str(wav), "rb") as sound:
            duration = sound.getnframes() / sound.getframerate()
        p95 = sorted(differences)[round(0.95 * (len(differences) - 1))]
        print("\t".join(map(str, (
            stem, len(old), len(new),
            sum(d <= .001 for d in differences), sum(d <= .05 for d in differences),
            sum(d <= .1 for d in differences),
            round(statistics.median(differences) * 1000, 3), round(p95 * 1000, 3),
            sum(time > duration for time, _ in old), round(duration, 3),
        ))))


if __name__ == "__main__":
    main()
