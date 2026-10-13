"""Standalone WAV-to-logits adapter for the frozen no-SMC TCN checkpoint."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .contracts import FrameActivations
from .tcn_model import BeatTCN


class TCNBackend:
    def __init__(self, *, checkpoint: Path, device: str, fps: float = 50.0):
        import torch
        from beat_this.inference import load_checkpoint
        from beat_this.preprocessing import LogMelSpect

        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(f"CUDA device requested but unavailable: {device}")
        state = load_checkpoint(str(checkpoint), device="cpu")
        params = state["hyper_parameters"]
        if params.get("architecture") != "tcn":
            raise ValueError("TCN checkpoint has the wrong architecture")
        if float(params.get("fps", fps)) != float(fps):
            raise ValueError("TCN checkpoint frame rate differs from registry")
        self.fps = float(fps)
        self.chunk_size = int(params.get("prediction_chunk_size", 1500))
        self.model = BeatTCN(
            spect_dim=int(params.get("spect_dim", 128)),
            channels=int(params.get("tcn_channels", 20)),
            kernel_size=int(params.get("tcn_kernel_size", 5)),
            dilations=tuple(params.get("tcn_dilations", (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024))),
            dropout=float(params.get("tcn_dropout", 0.15)),
            sum_head=bool(params.get("sum_head", False)),
            frequency_adapter=params.get("frequency_adapter", "madmom_74"),
            original_spect_dim=int(params.get("original_spect_dim", 74)),
        )
        weights = state["state_dict"]
        model_weights = {key.removeprefix("model."): value for key, value in weights.items() if key.startswith("model.")}
        if not model_weights:
            raise ValueError("TCN checkpoint contains no model weights")
        self.model.load_state_dict(model_weights, strict=True)
        self.model = self.model.to(self.device).eval()
        self.spect = LogMelSpect(device=self.device)

    def predict(self, audio_path: Path) -> FrameActivations:
        import soxr
        import torch
        from beat_this.inference import split_predict_aggregate
        from beat_this.preprocessing import load_audio

        signal, sample_rate = load_audio(audio_path)
        if signal.ndim == 2:
            signal = signal.mean(axis=1)
        elif signal.ndim != 1:
            raise ValueError("input WAV must be mono or stereo")
        if sample_rate != 22050:
            signal = soxr.resample(signal, in_rate=sample_rate, out_rate=22050)
        audio = torch.as_tensor(signal, dtype=torch.float32, device=self.device)
        with torch.inference_mode():
            spect = self.spect(audio)
            with torch.autocast(
                device_type=self.device.type, dtype=torch.float16,
                enabled=self.device.type == "cuda",
            ):
                prediction = split_predict_aggregate(
                    spect, chunk_size=self.chunk_size, border_size=6,
                    overlap_mode="keep_first", model=self.model,
                )
        return FrameActivations(
            np.asarray(prediction["beat"].float().cpu(), dtype=np.float64),
            np.asarray(prediction["downbeat"].float().cpu(), dtype=np.float64),
            self.fps,
        )
