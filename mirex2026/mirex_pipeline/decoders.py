"""Interchangeable Direct, DBN, and CASM postprocessors."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.special import expit

from .contracts import FrameActivations, FloatArray


class EventDecoder(Protocol):
    def decode(self, activations: FrameActivations) -> tuple[FloatArray, FloatArray]: ...


def _deduplicate(peaks: np.ndarray, width: int = 1) -> FloatArray:
    result: list[float] = []
    iterator = iter(map(int, peaks))
    try:
        peak = next(iterator)
    except StopIteration:
        return np.asarray(result, dtype=np.float64)
    count = 1
    for next_peak in iterator:
        if next_peak - peak <= width:
            count += 1
            peak += (next_peak - peak) / count
        else:
            result.append(float(peak))
            peak = next_peak
            count = 1
    result.append(float(peak))
    return np.asarray(result, dtype=np.float64)


def _local_maxima(values: FloatArray, kernel_size: int = 7) -> np.ndarray:
    pooled = maximum_filter1d(
        values, size=kernel_size, mode="constant", cval=-np.inf
    )
    return np.flatnonzero((values == pooled) & (values > 0.0))


def _snap_downbeats(beats: FloatArray, downbeats: FloatArray) -> FloatArray:
    if not len(downbeats):
        return np.empty(0, dtype=np.float64)
    # BeatThis keeps raw downbeat peaks in the degenerate no-beat case.
    if not len(beats):
        return np.asarray(downbeats, dtype=np.float64)
    return np.unique(
        np.asarray(
            [beats[np.argmin(np.abs(beats - value))] for value in downbeats],
            dtype=np.float64,
        )
    )


@dataclass(slots=True)
class DirectDecoder:
    """Exact NumPy equivalent of BeatThis's minimal postprocessor."""

    def decode(self, activations: FrameActivations) -> tuple[FloatArray, FloatArray]:
        beat_frames = _deduplicate(_local_maxima(activations.beat_logits))
        downbeat_frames = _deduplicate(_local_maxima(activations.downbeat_logits))
        beats = beat_frames / activations.fps
        return beats, _snap_downbeats(beats, downbeat_frames / activations.fps)


@dataclass(slots=True)
class DBNDecoder:
    """Joint madmom DBN with explicit tempo limits."""

    min_bpm: float = 55.0
    max_bpm: float = 215.0

    def decode(self, activations: FrameActivations) -> tuple[FloatArray, FloatArray]:
        try:
            from madmom.features.downbeats import DBNDownBeatTrackingProcessor
        except ImportError as exc:
            raise RuntimeError(
                "DBN decoding requires the pinned madmom dependency; run install.sh."
            ) from exc
        processor = DBNDownBeatTrackingProcessor(
            beats_per_bar=[3, 4],
            min_bpm=self.min_bpm,
            max_bpm=self.max_bpm,
            fps=activations.fps,
            transition_lambda=100.0,
            observation_lambda=16.0,
            threshold=0.05,
        )
        epsilon = 1e-5
        beat = expit(activations.beat_logits)
        downbeat = expit(activations.downbeat_logits)
        beat = beat * (1 - epsilon) + epsilon / 2
        downbeat = downbeat * (1 - epsilon) + epsilon / 2
        combined = np.column_stack(
            (np.maximum(beat - downbeat, epsilon / 2), downbeat)
        )
        output = np.asarray(processor(combined), dtype=np.float64)
        if not len(output):
            return np.empty(0), np.empty(0)
        beats = output[:, 0]
        return beats, output[output[:, 1] == 1, 0]


@dataclass(slots=True)
class CASMEventDecoder:
    config_path: Path
    _decoder: object = field(init=False, repr=False)

    def __post_init__(self) -> None:
        from casm_beat_tracking import CASMConfig, CASMDecoder

        self._decoder = CASMDecoder(CASMConfig.from_json(self.config_path))

    def decode(self, activations: FrameActivations) -> tuple[FloatArray, FloatArray]:
        beats, downbeats = self._decoder.decode(
            activations.beat_logits, activations.downbeat_logits
        )
        return (
            np.asarray(beats, dtype=np.float64),
            np.asarray(downbeats, dtype=np.float64),
        )


def make_decoder(
    name: str,
    *,
    casm_config: Path,
    dbn_bpm: tuple[float, float],
) -> EventDecoder:
    if name == "direct":
        return DirectDecoder()
    if name == "dbn":
        return DBNDecoder(*dbn_bpm)
    if name == "casm":
        return CASMEventDecoder(casm_config)
    raise ValueError(f"unsupported decoder: {name}")
