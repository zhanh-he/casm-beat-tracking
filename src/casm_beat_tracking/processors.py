"""Callable, madmom-style processor interfaces for CASM."""

from __future__ import annotations

from typing import Literal, cast

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .config import CASMConfig
from .decoder import CASMDecoder

FloatArray = NDArray[np.float64]
InputType = Literal["logits", "probabilities"]


def _validate_input_type(input_type: str) -> InputType:
    if input_type not in {"logits", "probabilities"}:
        raise ValueError("input_type must be 'logits' or 'probabilities'")
    return cast(InputType, input_type)


def _downbeat_indices(
    beats: FloatArray, downbeats: FloatArray, tolerance: float = 1e-9
) -> NDArray[np.int64]:
    """Locate downbeats in a sorted beat sequence in O(B + D log B)."""
    if not len(beats) or not len(downbeats):
        return np.empty(0, dtype=np.int64)

    found: list[int] = []
    for downbeat in downbeats:
        right = int(np.searchsorted(beats, downbeat))
        candidates = [index for index in (right - 1, right) if 0 <= index < len(beats)]
        nearest = min(candidates, key=lambda index: abs(beats[index] - downbeat))
        if abs(beats[nearest] - downbeat) <= tolerance:
            found.append(nearest)
    return np.unique(np.asarray(found, dtype=np.int64))


def beat_numbers(beats: ArrayLike, downbeats: ArrayLike) -> NDArray[np.int64]:
    """Return natural beat-in-bar numbers, with each downbeat numbered one."""
    beat_array = np.asarray(beats, dtype=np.float64)
    downbeat_array = np.asarray(downbeats, dtype=np.float64)
    if beat_array.ndim != 1 or downbeat_array.ndim != 1:
        raise ValueError("beat and downbeat times must be one-dimensional")
    if not np.all(np.isfinite(beat_array)) or not np.all(
        np.isfinite(downbeat_array)
    ):
        raise ValueError("beat and downbeat times must be finite")
    if np.any(np.diff(beat_array) < 0) or np.any(np.diff(downbeat_array) < 0):
        raise ValueError("beat and downbeat times must be sorted")
    if not len(beat_array):
        return np.empty(0, dtype=np.int64)

    indices = _downbeat_indices(beat_array, downbeat_array)
    downbeat_set = set(map(int, indices))
    if len(indices) >= 2:
        meter = int(indices[1] - indices[0])
        pickup = int(indices[0])
        counter = meter - pickup if 0 < pickup < meter else 0
    else:
        counter = 0

    numbers = np.empty(len(beat_array), dtype=np.int64)
    for index in range(len(beat_array)):
        if index in downbeat_set:
            counter = 1
        else:
            counter += 1
        numbers[index] = counter
    return numbers


def events_from_times(beats: ArrayLike, downbeats: ArrayLike) -> FloatArray:
    """Return the conventional ``[time_seconds, beat_number]`` event matrix."""
    beat_array = np.asarray(beats, dtype=np.float64)
    numbers = beat_numbers(beat_array, downbeats)
    if not len(beat_array):
        return np.empty((0, 2), dtype=np.float64)
    return np.column_stack((beat_array, numbers)).astype(np.float64, copy=False)


class CASMBeatTrackingProcessor:
    """Callable beat tracker for a one-dimensional activation function.

    This intentionally mirrors madmom's processor ergonomics: construct once,
    then call the object or its :meth:`process` method. It is a postprocessor,
    not an audio frontend, and therefore expects framewise activations.
    """

    def __init__(
        self,
        config: CASMConfig | None = None,
        *,
        input_type: InputType = "probabilities",
        **overrides: object,
    ) -> None:
        self.input_type = _validate_input_type(input_type)
        self.decoder = CASMDecoder(config, **overrides)

    @property
    def fps(self) -> float:
        return self.decoder.fps

    def __call__(self, activations: ArrayLike, **kwargs: object) -> FloatArray:
        return self.process(activations, **kwargs)

    def process(self, activations: ArrayLike, **kwargs: object) -> FloatArray:
        """Decode beat activations and return event times in seconds."""
        input_type = _validate_input_type(
            str(kwargs.pop("input_type", self.input_type))
        )
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"unexpected process keyword argument(s): {names}")
        beat_values = np.asarray(activations)
        if beat_values.ndim != 1:
            raise ValueError("beat activations must be one-dimensional")
        silent_downbeats = np.zeros_like(beat_values)
        beats, _ = self.decoder.decode(
            beat_values, silent_downbeats, input_type=input_type
        )
        return beats


class CASMDownBeatTrackingProcessor:
    """Decode ``(frames, 2)`` beat/downbeat activations into timed events.

    Column 0 contains beat activations and column 1 contains downbeat
    activations. The result has shape ``(num_beats, 2)`` with time in seconds
    and natural beat-in-bar numbering, matching the common madmom convention.
    """

    def __init__(
        self,
        config: CASMConfig | None = None,
        *,
        input_type: InputType = "probabilities",
        **overrides: object,
    ) -> None:
        self.input_type = _validate_input_type(input_type)
        self.decoder = CASMDecoder(config, **overrides)

    @property
    def fps(self) -> float:
        return self.decoder.fps

    def __call__(self, activations: ArrayLike, **kwargs: object) -> FloatArray:
        return self.process(activations, **kwargs)

    def process(self, activations: ArrayLike, **kwargs: object) -> FloatArray:
        """Return a ``[time_seconds, beat_number]`` matrix."""
        input_type = _validate_input_type(
            str(kwargs.pop("input_type", self.input_type))
        )
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"unexpected process keyword argument(s): {names}")
        values = np.asarray(activations)
        if values.ndim != 2 or values.shape[1] != 2:
            raise ValueError("activations must have shape (frames, 2)")
        beats, downbeats = self.decoder.decode(
            values[:, 0], values[:, 1], input_type=input_type
        )
        return events_from_times(beats, downbeats)


class CASMProcessor(CASMDownBeatTrackingProcessor):
    """Short alias for :class:`CASMDownBeatTrackingProcessor`."""
