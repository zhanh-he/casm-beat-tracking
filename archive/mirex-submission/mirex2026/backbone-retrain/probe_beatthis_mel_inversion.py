#!/usr/bin/env python3
"""Paired-audio feasibility probe for using BeatThis log-Mel with frozen MERT.

Use an allowed training song with *both* its verified WAV and released
spectrogram. This reconstructs one 15 s crop with inverse Mel + Griffin-Lim
and compares the re-encoded Mel plus frozen MERT features. It never calls
SMC/GTZAN and is not a BeatFM training or accuracy result.
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
    parser.add_argument("--mert-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--iterations", type=int, default=32)
    args = parser.parse_args()
    import torch
    import torchaudio
    from torch.nn.functional import cosine_similarity
    from transformers import AutoModel

    torch.set_num_threads(4)
    device = torch.device(args.device)
    signal, rate = torchaudio.load(str(args.audio))
    signal = signal.float().mean(dim=0)
    signal_22050 = torchaudio.functional.resample(signal, rate, 22_050)
    length = 15 * 22_050
    signal_22050 = signal_22050[:length]
    if len(signal_22050) < length:
        raise ValueError("paired audio is shorter than 15 seconds")
    cached = torch.from_numpy(np.load(args.logmel_npy)[:751].astype("float32")).T.to(device)
    if cached.shape != (128, 751):
        raise ValueError(f"unexpected BeatThis 15-second crop shape: {tuple(cached.shape)}")
    forward = torchaudio.transforms.MelSpectrogram(
        sample_rate=22_050, n_fft=1024, hop_length=441, f_min=30,
        f_max=11_000, n_mels=128, mel_scale="slaney",
        normalized="frame_length", power=1,
    ).to(device)
    original_logmel = torch.log1p(1000 * forward(signal_22050.to(device)))
    cached_vs_audio_mae = (cached - original_logmel).abs().mean().item()
    mel_magnitude = torch.expm1(cached) / 1000
    inverse_mel = torchaudio.transforms.InverseMelScale(
        n_stft=513, n_mels=128, sample_rate=22_050,
        f_min=30, f_max=11_000, mel_scale="slaney",
    ).to(device)
    # BeatThis STFT used frame_length normalization, i.e. /sqrt(n_fft).
    linear_magnitude = inverse_mel(mel_magnitude) * 1024**0.5
    griffin_lim = torchaudio.transforms.GriffinLim(
        n_fft=1024, hop_length=441, n_iter=args.iterations,
        power=1, length=length, rand_init=False,
    ).to(device)
    reconstructed = griffin_lim(linear_magnitude.clamp_min(0))
    reconstructed_logmel = torch.log1p(1000 * forward(reconstructed)[:, :751])
    mel_reconstruction_mae = (cached - reconstructed_logmel).abs().mean().item()
    original_24k = torchaudio.functional.resample(signal_22050, 22_050, 24_000)
    reconstructed_24k = torchaudio.functional.resample(reconstructed.cpu(), 22_050, 24_000)
    model = AutoModel.from_pretrained(
        str(args.mert_dir), output_hidden_states=True, trust_remote_code=True,
    ).to(device).eval()
    with torch.inference_mode():
        original_states = model(original_24k.unsqueeze(0).to(device)).hidden_states[1:]
        reconstructed_states = model(reconstructed_24k.unsqueeze(0).to(device)).hidden_states[1:]
        cosines = [float(cosine_similarity(a.float(), b.float(), dim=-1).mean())
                   for a, b in zip(original_states, reconstructed_states)]
    print(json.dumps({
        "audio": str(args.audio),
        "logmel_npy": str(args.logmel_npy),
        "cached_vs_original_logmel_mae": cached_vs_audio_mae,
        "cached_vs_reconstructed_logmel_mae": mel_reconstruction_mae,
        "mert_layer_cosine_mean": cosines,
        "griffin_lim_iterations": args.iterations,
        "waveform_reconstruction_is_original_audio": False,
    }, indent=2))


if __name__ == "__main__":
    main()
