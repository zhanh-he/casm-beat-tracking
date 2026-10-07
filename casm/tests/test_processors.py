from __future__ import annotations

import json
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path

import numpy as np
import pytest
from scipy.special import expit

from casm_beat_tracking import (
    CASMBeatTrackingProcessor,
    CASMDecoder,
    CASMDownBeatTrackingProcessor,
    CASMProcessor,
    __version__,
    beat_numbers,
)


def regular_logits(length: int = 401) -> tuple[np.ndarray, np.ndarray]:
    beat = np.full(length, -6.0)
    downbeat = np.full(length, -6.0)
    beat[np.arange(0, length, 25)] = 6.0
    downbeat[np.arange(0, length, 100)] = 6.0
    return beat, downbeat


def test_madmom_style_processor_is_callable() -> None:
    beat, downbeat = regular_logits()
    activations = np.column_stack((expit(beat), expit(downbeat)))
    events = CASMDownBeatTrackingProcessor()(activations)
    expected_beats, expected_downbeats = CASMDecoder().decode(beat, downbeat)

    assert events.shape == (len(expected_beats), 2)
    np.testing.assert_allclose(events[:, 0], expected_beats)
    assert set(events[:, 1]).issuperset({1.0, 2.0, 3.0, 4.0})
    for event in expected_downbeats:
        index = int(np.argmin(np.abs(events[:, 0] - event)))
        assert events[index, 1] == 1.0


def test_short_alias_and_per_call_input_override() -> None:
    beat, downbeat = regular_logits()
    logits = np.column_stack((beat, downbeat))
    long_name = CASMDownBeatTrackingProcessor(input_type="logits").process(logits)
    short_name = CASMProcessor()(logits, input_type="logits")
    np.testing.assert_array_equal(long_name, short_name)


def test_beat_only_processor_matches_decoder() -> None:
    beat, _ = regular_logits()
    actual = CASMBeatTrackingProcessor(input_type="logits")(beat)
    expected, _ = CASMDecoder().decode(beat, np.zeros_like(beat))
    np.testing.assert_array_equal(actual, expected)


def test_processor_rejects_ambiguous_shapes_and_keywords() -> None:
    processor = CASMProcessor()
    with pytest.raises(ValueError, match="shape"):
        processor(np.zeros(10))
    with pytest.raises(TypeError, match="unexpected"):
        processor(np.zeros((10, 2)), online=True)


def test_pickup_numbering_and_time_validation() -> None:
    beats = np.arange(7, dtype=float)
    np.testing.assert_array_equal(
        beat_numbers(beats, np.asarray([1.0, 5.0])),
        np.asarray([4, 1, 2, 3, 4, 1, 2]),
    )
    with pytest.raises(ValueError, match="sorted"):
        beat_numbers([1.0, 0.0], [])


def test_wheel_contains_the_frozen_default() -> None:
    packaged = json.loads(
        files("casm_beat_tracking")
        .joinpath("data/casm-7f-default.json")
        .read_text(encoding="utf-8")
    )
    repository = json.loads(
        (Path(__file__).parents[1] / "config/casm-7f-default.json").read_text()
    )
    assert packaged == repository
    assert version("casm-beat-tracking") == __version__
