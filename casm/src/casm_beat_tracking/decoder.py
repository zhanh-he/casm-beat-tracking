"""Confidence-adaptive semi-Markov beat and downbeat decoding."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.ndimage import maximum_filter1d, median_filter, uniform_filter1d
from scipy.signal import find_peaks
from scipy.special import expit

from .config import CASMConfig, DEFAULT_CONFIG

FloatArray = NDArray[np.float64]


def _deduplicate_peaks(peaks: NDArray[np.integer], width: int = 1) -> FloatArray:
    result: list[float] = []
    iterator = iter(map(int, peaks))
    try:
        peak = float(next(iterator))
    except StopIteration:
        return np.empty(0, dtype=np.float64)
    count = 1
    for next_peak in iterator:
        if next_peak - peak <= width:
            count += 1
            peak += (next_peak - peak) / count
        else:
            result.append(peak)
            peak = float(next_peak)
            count = 1
    result.append(peak)
    return np.asarray(result, dtype=np.float64)


def _local_maxima(
    values: FloatArray, kernel_size: int = 7, threshold: float = 0.0
) -> NDArray[np.int64]:
    pooled = maximum_filter1d(
        values, size=kernel_size, mode="constant", cval=-1000.0
    )
    return np.flatnonzero((values == pooled) & (values > threshold))


def _edge_local_maxima(values: FloatArray) -> NDArray[np.int64]:
    peaks, _ = find_peaks(values)
    extra: list[int] = []
    if len(values) == 1:
        extra.append(0)
    elif len(values):
        if values[0] >= values[1]:
            extra.append(0)
        if values[-1] >= values[-2]:
            extra.append(len(values) - 1)
    if not extra:
        return peaks.astype(np.int64, copy=False)
    return np.unique(np.concatenate((peaks, np.asarray(extra, dtype=np.int64))))


def _snap_downbeats_to_beats(
    beat_times: FloatArray, downbeat_times: FloatArray
) -> FloatArray:
    if not len(beat_times) or not len(downbeat_times):
        return np.empty(0, dtype=np.float64)
    snapped = [
        beat_times[np.argmin(np.abs(beat_times - time))] for time in downbeat_times
    ]
    return np.unique(np.asarray(snapped, dtype=np.float64))


def _event_f_measure(
    reference: FloatArray, estimate: FloatArray, tolerance: float
) -> float:
    if not len(reference) and not len(estimate):
        return 1.0
    if not len(reference) or not len(estimate):
        return 0.0
    reference_index = estimate_index = matches = 0
    while reference_index < len(reference) and estimate_index < len(estimate):
        delta = reference[reference_index] - estimate[estimate_index]
        if abs(delta) <= tolerance:
            matches += 1
            reference_index += 1
            estimate_index += 1
        elif delta < 0:
            reference_index += 1
        else:
            estimate_index += 1
    if not matches:
        return 0.0
    precision = matches / len(estimate)
    recall = matches / len(reference)
    return 2.0 * precision * recall / (precision + recall)


def _local_period_score_matrix(
    probabilities: FloatArray,
    candidate_frames: NDArray[np.int64],
    config: CASMConfig,
) -> tuple[NDArray[np.int64], NDArray[np.float32]]:
    """Compute normalized local autocorrelation without a dense state lattice."""
    min_lag = max(2, int(np.ceil(config.fps * 60.0 / config.max_bpm)))
    max_lag = min(
        len(probabilities) - 1,
        int(np.floor(config.fps * 60.0 / config.min_bpm)),
    )
    if max_lag < min_lag or not len(candidate_frames):
        return (
            np.empty(0, dtype=np.int64),
            np.empty((0, len(candidate_frames)), dtype=np.float32),
        )

    lags = np.arange(min_lag, max_lag + 1, dtype=np.int64)
    window = max(3, int(round(config.local_window_seconds * config.fps)))
    energy = uniform_filter1d(
        probabilities * probabilities, size=window, mode="constant"
    )
    scores = np.empty((len(lags), len(candidate_frames)), dtype=np.float32)
    shifted = np.zeros_like(probabilities)
    for row, lag in enumerate(lags):
        shifted.fill(0.0)
        shifted[lag:] = probabilities[:-lag]
        cross = uniform_filter1d(
            probabilities * shifted, size=window, mode="constant"
        )
        shifted_energy = uniform_filter1d(
            shifted * shifted, size=window, mode="constant"
        )
        normalized = cross / np.sqrt(energy * shifted_energy + 1e-8)
        bias = (min_lag / lag) ** config.tempo_bias
        scores[row] = normalized[candidate_frames] * bias
    return lags, scores


def _estimate_local_periods(
    probabilities: FloatArray,
    candidate_frames: NDArray[np.int64],
    config: CASMConfig,
) -> tuple[FloatArray, FloatArray]:
    lags, scores = _local_period_score_matrix(
        probabilities, candidate_frames, config
    )
    if not len(lags):
        fallback = max(2, int(np.ceil(config.fps * 60.0 / config.max_bpm)))
        return (
            np.full(len(candidate_frames), fallback, dtype=np.float64),
            np.zeros(len(candidate_frames), dtype=np.float64),
        )

    best_rows = np.argmax(scores, axis=0)
    columns = np.arange(scores.shape[1])
    best_scores = scores[best_rows, columns]
    if len(lags) == 1:
        confidence = np.ones(len(candidate_frames), dtype=np.float64)
    else:
        second_scores = np.empty_like(best_scores)
        for column, best_row in enumerate(best_rows):
            alternatives = scores[:, column].copy()
            alternatives[max(0, best_row - 2) : best_row + 3] = -np.inf
            if np.all(~np.isfinite(alternatives)):
                second_scores[column] = -np.inf
            else:
                second_scores[column] = np.max(alternatives)
        confidence = np.ones(len(candidate_frames), dtype=np.float64)
        finite = np.isfinite(second_scores)
        confidence[finite] = np.clip(
            (best_scores[finite] - second_scores[finite])
            / (np.abs(best_scores[finite]) + 1e-6),
            0.0,
            1.0,
        )

    periods = lags[best_rows].astype(np.float64)
    if len(periods) >= 5:
        periods = median_filter(periods, size=5, mode="nearest")
        confidence = median_filter(confidence, size=5, mode="nearest")
    return periods, confidence


class CASMDecoder:
    """Decode 50 Hz beat/downbeat activations with the frozen 7F setting.

    CASM has no learned weights. Its dynamic program runs only over local
    activation maxima, avoiding the dense tempo/meter state lattice used by a
    conventional DBN decoder.
    """

    def __init__(
        self,
        config: CASMConfig | None = None,
        **overrides: object,
    ) -> None:
        base = DEFAULT_CONFIG if config is None else config
        self.config = base.with_overrides(**overrides) if overrides else base

    @property
    def fps(self) -> float:
        return self.config.fps

    def decode(
        self,
        beat_values: ArrayLike,
        downbeat_values: ArrayLike,
        *,
        input_type: Literal["logits", "probabilities"] = "logits",
    ) -> tuple[FloatArray, FloatArray]:
        """Return beat and downbeat times in seconds.

        Both inputs must be finite one-dimensional arrays of equal length.
        ``input_type='probabilities'`` accepts values in ``[0, 1]`` and maps
        them to logits before applying the same frozen decoder.
        """
        beat_logits = self._as_logits(beat_values, input_type, "beat")
        downbeat_logits = self._as_logits(
            downbeat_values, input_type, "downbeat"
        )
        if beat_logits.shape != downbeat_logits.shape:
            raise ValueError("beat and downbeat arrays must have equal length")
        if not len(beat_logits):
            return np.empty(0, dtype=np.float64), np.empty(0, dtype=np.float64)

        config = self.config
        beat_probabilities = expit(beat_logits)
        candidates = _edge_local_maxima(beat_probabilities)
        candidates = candidates[
            beat_probabilities[candidates] >= config.candidate_threshold
        ]
        if not len(candidates):
            return np.empty(0, dtype=np.float64), np.empty(0, dtype=np.float64)

        direct_frames = _deduplicate_peaks(_local_maxima(beat_logits))
        periods, confidence = _estimate_local_periods(
            beat_probabilities, candidates, config
        )
        selected_frames = self._decode_beats(
            beat_logits, candidates, periods, confidence
        )
        if len(direct_frames):
            count_ratio = len(selected_frames) / len(direct_frames)
            if not (
                config.fallback_minimal_ratio
                <= count_ratio
                <= config.fallback_maximal_ratio
            ):
                selected_frames = direct_frames

        beat_times = selected_frames / config.fps
        raw_downbeat_frames = _deduplicate_peaks(_local_maxima(downbeat_logits))
        direct_downbeat_times = _snap_downbeats_to_beats(
            beat_times, raw_downbeat_frames / config.fps
        )
        if config.downbeat_mode == "snap":
            return beat_times, direct_downbeat_times

        downbeat_frames = self._decode_downbeats(
            selected_frames, downbeat_logits
        )
        downbeat_times = downbeat_frames / config.fps
        if (
            config.downbeat_agreement_threshold > 0
            and _event_f_measure(
                direct_downbeat_times,
                downbeat_times,
                config.downbeat_agreement_tolerance,
            )
            < config.downbeat_agreement_threshold
        ):
            downbeat_times = direct_downbeat_times
        return beat_times, downbeat_times

    @staticmethod
    def _as_logits(
        values: ArrayLike,
        input_type: Literal["logits", "probabilities"],
        name: str,
    ) -> FloatArray:
        array = np.asarray(values, dtype=np.float64)
        if array.ndim != 1:
            raise ValueError(f"{name} values must be one-dimensional")
        if not np.all(np.isfinite(array)):
            raise ValueError(f"{name} values must be finite")
        if input_type == "logits":
            return array
        if input_type != "probabilities":
            raise ValueError("input_type must be 'logits' or 'probabilities'")
        if np.any((array < 0.0) | (array > 1.0)):
            raise ValueError(f"{name} probabilities must lie in [0, 1]")
        epsilon = np.finfo(np.float64).eps
        clipped = np.clip(array, epsilon, 1.0 - epsilon)
        return np.log(clipped) - np.log1p(-clipped)

    def _decode_beats(
        self,
        logits: FloatArray,
        candidates: NDArray[np.int64],
        periods: FloatArray,
        confidence: FloatArray,
    ) -> FloatArray:
        config = self.config
        min_interval = int(np.ceil(config.fps * 60.0 / config.max_bpm))
        max_interval = int(np.floor(config.fps * 60.0 / config.min_bpm))
        node_scores = np.clip(
            logits[candidates] / config.temperature,
            -config.logit_clip,
            config.logit_clip,
        )
        scores = node_scores.copy()
        previous = np.full(len(candidates), -1, dtype=np.int64)

        left = 0
        for end in range(len(candidates)):
            while left < end and candidates[end] - candidates[left] > max_interval:
                left += 1
            starts = np.arange(left, end, dtype=np.int64)
            if not len(starts):
                continue
            intervals = candidates[end] - candidates[starts]
            starts = starts[intervals >= min_interval]
            if not len(starts):
                continue
            intervals = (candidates[end] - candidates[starts]).astype(np.float64)
            expected = np.sqrt(periods[end] * periods[starts])
            segment_confidence = np.sqrt(confidence[end] * confidence[starts])
            sigma = config.duration_sigma + (
                1.0 - segment_confidence
            ) * config.uncertain_sigma
            log_error = np.log(np.maximum(intervals, 1.0) / expected)
            duration_cost = (
                config.duration_weight
                * segment_confidence
                * 0.5
                * (log_error / sigma) ** 2
            )
            transition_scores = scores[starts] - duration_cost
            best_offset = int(np.argmax(transition_scores))
            best_score = float(transition_scores[best_offset])
            if best_score > 0:
                scores[end] += best_score
                previous[end] = starts[best_offset]

        end = int(np.argmax(scores))
        path: list[int] = []
        while end >= 0:
            path.append(end)
            end = int(previous[end])
        return candidates[np.asarray(path[::-1], dtype=np.int64)].astype(np.float64)

    def _decode_downbeats(
        self, beat_frames: FloatArray, downbeat_logits: FloatArray
    ) -> FloatArray:
        if not len(beat_frames):
            return np.empty(0, dtype=np.float64)
        config = self.config
        integer_frames = np.clip(
            np.rint(beat_frames).astype(np.int64), 0, len(downbeat_logits) - 1
        )
        node_scores = (
            np.clip(
                downbeat_logits[integer_frames] / config.downbeat_temperature,
                -config.logit_clip,
                config.logit_clip,
            )
            + config.bar_reward
        )
        meter_values = np.asarray(config.meters, dtype=np.int64)
        scores = np.full((len(beat_frames), len(meter_values)), -np.inf)
        previous_meter = np.full(scores.shape, -1, dtype=np.int64)

        for beat_index in range(len(beat_frames)):
            for meter_index, meter in enumerate(meter_values):
                previous_beat = beat_index - meter
                if previous_beat < 0:
                    if beat_index < meter_values.max():
                        scores[beat_index, meter_index] = node_scores[beat_index]
                    continue
                prior = scores[previous_beat].copy()
                prior -= config.meter_change_penalty * (meter_values != meter)
                best_previous_meter = int(np.argmax(prior))
                if np.isfinite(prior[best_previous_meter]):
                    scores[beat_index, meter_index] = (
                        node_scores[beat_index] + prior[best_previous_meter]
                    )
                    previous_meter[beat_index, meter_index] = best_previous_meter

        tail_start = max(0, len(beat_frames) - meter_values.max())
        tail_scores = scores[tail_start:]
        tail_beat, meter_index = np.unravel_index(
            int(np.argmax(tail_scores)), tail_scores.shape
        )
        beat_index = tail_start + tail_beat
        path: list[int] = []
        while beat_index >= 0:
            path.append(beat_index)
            previous = previous_meter[beat_index, meter_index]
            meter = meter_values[meter_index]
            beat_index -= meter
            if previous < 0:
                break
            meter_index = int(previous)
        return beat_frames[np.asarray(path[::-1], dtype=np.int64)]
