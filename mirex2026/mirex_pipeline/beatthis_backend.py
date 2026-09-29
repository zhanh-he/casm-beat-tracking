"""BeatThis audio frontend adapter."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .contracts import FrameActivations


class BeatThisBackend:
    def __init__(self, *, checkpoint: Path, device: str, fps: float = 50.0):
        import torch
        from beat_this.inference import Audio2Frames

        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        resolved = torch.device(device)
        if resolved.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(f"CUDA device requested but unavailable: {device}")
        self.device = resolved
        self.fps = float(fps)
        self.frontend = Audio2Frames(
            checkpoint_path=str(checkpoint),
            device=resolved,
            float16=resolved.type == "cuda",
        )

    def predict(self, audio_path: Path) -> FrameActivations:
        from beat_this.preprocessing import load_audio

        signal, sample_rate = load_audio(audio_path)
        beat, downbeat = self.frontend(signal, sample_rate)
        return FrameActivations(
            np.asarray(beat.detach().cpu(), dtype=np.float64),
            np.asarray(downbeat.detach().cpu(), dtype=np.float64),
            self.fps,
        )
