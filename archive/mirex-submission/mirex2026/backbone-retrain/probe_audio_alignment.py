#!/usr/bin/env python3
"""Check time alignment of a candidate recording to BeatThis's cached Mel.

This diagnostic uses only a permitted source piece. A matching title or near-
matching duration is insufficient: the release used particular recordings.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--logmel-npy", type=Path, required=True)
    parser.add_argument("--max-shift-seconds", type=float, default=10)
    args = parser.parse_args()
    import torch
    import torchaudio

    torch.set_num_threads(4)
    samples, rate = torchaudio.load(str(args.audio))
    samples = samples.float().mean(dim=0)
    samples = torchaudio.functional.resample(samples, rate, 22_050)
    transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=22_050, n_fft=1024, hop_length=441, f_min=30,
        f_max=11_000, n_mels=128, mel_scale="slaney",
        normalized="frame_length", power=1,
    )
    with torch.no_grad():
        current = torch.log1p(1000 * transform(samples)).T.numpy()
    cached = np.load(args.logmel_npy).astype(np.float32)
    if cached.ndim != 2 or cached.shape[1] != 128:
        raise ValueError(f"unexpected cached spectrogram: {cached.shape}")
    # 32 kbps MP3 loses upper frequencies; search timing using the retained band.
    reference = cached[250:min(len(cached), 2250), 4:80]
    ref_norm = (reference - reference.mean(axis=0)) / (reference.std(axis=0) + 1e-5)
    max_shift = round(args.max_shift_seconds * 50)
    results: list[tuple[float, float, int]] = []
    for lag in range(-max_shift, max_shift + 1):
        start = 250 + lag
        if start < 0 or start + len(reference) > len(current):
            continue
        candidate = current[start:start + len(reference), 4:80]
        # Normalize each frequency independently, then measure temporal match.
        cand_norm = (candidate - candidate.mean(axis=0)) / (candidate.std(axis=0) + 1e-5)
        correlation = float((ref_norm * cand_norm).mean())
        mae = float(np.abs(reference - candidate).mean())
        results.append((correlation, mae, lag))
    if not results:
        raise ValueError("audio is too short for the selected search window")
    best = max(results)
    zero = next((row for row in results if row[2] == 0), None)
    print(json.dumps({
        "audio": str(args.audio),
        "cached_duration_seconds": len(cached) / 50,
        "candidate_duration_seconds": len(samples) / 22_050,
        "zero_shift_correlation": None if zero is None else zero[0],
        "zero_shift_logmel_mae": None if zero is None else zero[1],
        "best_shift_seconds_audio_minus_cache": best[2] / 50,
        "best_shift_correlation": best[0],
        "best_shift_logmel_mae": best[1],
    }, indent=2))


if __name__ == "__main__":
    main()
