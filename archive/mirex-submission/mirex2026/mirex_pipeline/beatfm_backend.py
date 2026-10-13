"""Frozen-MERT BeatFM inference adapter for one MIREX WAV.

The supplied BeatFM source and MERT weights are deliberately not vendored in
this repository. Set BEATFM_SOURCE_DIR and BEATFM_MERT_DIR to audited local
copies. A pilot checkpoint requires an explicit smoke-only override.
"""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import math
import os
from pathlib import Path

import numpy as np

from .contracts import FrameActivations


SOURCE_ZIP_SHA256 = "4fbf554a78f2f353d1461f2267fa45f43b6cf864fc423f146ae46d301018858a"
MERT_REVISION = "12af15fef9d0ac838c3f475bfbbf26d2060dd4f5"
INPUT_RATE = 24_000
SOURCE_FPS = 75.0
CLIP_SAMPLES = 15 * INPUT_RATE
HOP_SAMPLES = 10 * INPUT_RATE


def _training_module():
    path = Path(__file__).resolve().parent.parent / "backbone-retrain" / "train_beatfm.py"
    spec = importlib.util.spec_from_file_location("mirex_train_beatfm", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load BeatFM architecture from {path}")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _verify_source(payload: dict, source_dir: Path) -> None:
    recipe = payload.get("recipe") or {}
    smoke_pilot = bool(recipe.get("pilot_partial_audio_not_submission")) and os.environ.get("BEATFM_ALLOW_PILOT_FOR_SMOKE") == "1"
    if payload.get("source_zip_sha256") != SOURCE_ZIP_SHA256:
        raise ValueError("BeatFM checkpoint source archive does not match the audited ZIP")
    if payload.get("mert_revision") != MERT_REVISION:
        raise ValueError("BeatFM checkpoint MERT revision does not match")
    for key, filename in (("source_msa_sha256", "MultilevelSemanticAggregation.py"),
                          ("source_model_sha256", "model.py")):
        actual = sha256((source_dir / filename).read_bytes()).hexdigest()
        # The first engineering pilot predates file-level checkpoint hashes.
        # It may be loaded only for an explicitly opt-in inference smoke test.
        if payload.get(key) is None and smoke_pilot:
            continue
        if payload.get(key) != actual:
            raise ValueError(f"BeatFM checkpoint/source mismatch: {filename}")
    if recipe.get("pilot_partial_audio_not_submission") and not smoke_pilot:
        raise ValueError("engineering-pilot BeatFM checkpoint is not a submission model")


def merge_clip_logits(clips: list[tuple[int, np.ndarray, np.ndarray]],
                      output_frames: int) -> tuple[np.ndarray, np.ndarray]:
    """Average overlapping 75 Hz logits; retain only frames inside audio."""
    beat = np.zeros(output_frames, dtype=np.float64)
    downbeat = np.zeros(output_frames, dtype=np.float64)
    count = np.zeros(output_frames, dtype=np.int32)
    for start, beat_clip, downbeat_clip in clips:
        if beat_clip.ndim != 1 or downbeat_clip.shape != beat_clip.shape:
            raise ValueError("BeatFM clip logits must have equal one-dimensional shapes")
        stop = min(output_frames, start + len(beat_clip))
        if start < 0 or start >= stop:
            continue
        length = stop - start
        beat[start:stop] += beat_clip[:length]
        downbeat[start:stop] += downbeat_clip[:length]
        count[start:stop] += 1
    if np.any(count == 0):
        raise ValueError("BeatFM sliding windows left uncovered audio frames")
    return beat / count, downbeat / count


def resample_logits(values: np.ndarray, source_fps: float, target_fps: float,
                    duration_seconds: float) -> np.ndarray:
    if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("invalid source-frame logits")
    output_frames = max(1, math.ceil(duration_seconds * target_fps))
    return np.interp(
        np.arange(output_frames, dtype=np.float64) / target_fps,
        np.arange(len(values), dtype=np.float64) / source_fps,
        values,
    )


class BeatFMBackend:
    """Return 50 Hz beat/downbeat logits for Direct, DBN, or CASM."""

    def __init__(self, *, checkpoint: Path, device: str, fps: float = 50.0):
        import torch

        source_env = os.environ.get("BEATFM_SOURCE_DIR")
        mert_env = os.environ.get("BEATFM_MERT_DIR")
        if not source_env or not mert_env:
            raise RuntimeError("set BEATFM_SOURCE_DIR and BEATFM_MERT_DIR to audited private copies")
        source_dir, mert_dir = Path(source_env), Path(mert_env)
        if not source_dir.is_dir() or not mert_dir.is_dir():
            raise FileNotFoundError("BeatFM source or MERT directory is missing")
        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(f"CUDA device requested but unavailable: {device}")
        self.fps = float(fps)
        if self.fps <= 0:
            raise ValueError("output FPS must be positive")
        payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
        if not isinstance(payload, dict) or "head_state_dict" not in payload:
            raise ValueError("invalid BeatFM checkpoint")
        _verify_source(payload, source_dir)
        module = _training_module()
        self.mert, self.head = module.build_model(source_dir, mert_dir, self.device)
        self.head.load_state_dict(payload["head_state_dict"], strict=True)
        self.mert.eval()
        self.head.eval()

    def predict(self, audio_path: Path) -> FrameActivations:
        import torch
        import torchaudio

        waveform, sample_rate = torchaudio.load(str(audio_path))
        if waveform.ndim != 2 or waveform.shape[-1] == 0:
            raise ValueError(f"empty or invalid WAV: {audio_path}")
        waveform = waveform.float().mean(dim=0)
        if sample_rate != INPUT_RATE:
            waveform = torchaudio.functional.resample(waveform, sample_rate, INPUT_RATE)
        duration = waveform.numel() / INPUT_RATE
        output_frames_75 = max(1, math.ceil(duration * SOURCE_FPS))
        clip_outputs: list[tuple[int, np.ndarray, np.ndarray]] = []
        with torch.inference_mode():
            for start in range(0, waveform.numel(), HOP_SAMPLES):
                clip = waveform[start:start + CLIP_SAMPLES]
                if clip.numel() < CLIP_SAMPLES:
                    clip = torch.nn.functional.pad(clip, (0, CLIP_SAMPLES - clip.numel()))
                hidden = self.mert(clip.unsqueeze(0).to(self.device)).hidden_states[1:]
                beat, downbeat = self.head(hidden)
                frame_start = round(start * SOURCE_FPS / INPUT_RATE)
                clip_outputs.append((
                    frame_start,
                    beat[0, 0].float().cpu().numpy().astype(np.float64),
                    downbeat[0, 0].float().cpu().numpy().astype(np.float64),
                ))
        beat_75, downbeat_75 = merge_clip_logits(clip_outputs, output_frames_75)
        return FrameActivations(
            resample_logits(beat_75, SOURCE_FPS, self.fps, duration),
            resample_logits(downbeat_75, SOURCE_FPS, self.fps, duration),
            self.fps,
        )
