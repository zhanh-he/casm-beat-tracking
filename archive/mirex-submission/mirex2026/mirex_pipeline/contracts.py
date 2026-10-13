"""Small contracts shared by all MIREX backbones and decoders."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class FrameActivations:
    """Beat/downbeat logits sampled at a fixed frame rate."""

    beat_logits: FloatArray
    downbeat_logits: FloatArray
    fps: float = 50.0

    def __post_init__(self) -> None:
        beat = np.asarray(self.beat_logits, dtype=np.float64)
        downbeat = np.asarray(self.downbeat_logits, dtype=np.float64)
        if beat.ndim != 1 or downbeat.ndim != 1:
            raise ValueError("beat and downbeat logits must be one-dimensional")
        if beat.shape != downbeat.shape:
            raise ValueError("beat and downbeat logits must have equal length")
        if not np.all(np.isfinite(beat)) or not np.all(np.isfinite(downbeat)):
            raise ValueError("beat and downbeat logits must be finite")
        if self.fps <= 0:
            raise ValueError("fps must be positive")
        object.__setattr__(self, "beat_logits", beat)
        object.__setattr__(self, "downbeat_logits", downbeat)
