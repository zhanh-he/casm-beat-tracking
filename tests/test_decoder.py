from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.special import expit

from casm_beat_tracking import CASMConfig, CASMDecoder
from casm_beat_tracking.cli import _infer_beat_numbers, main


def regular_logits(length: int = 401) -> tuple[np.ndarray, np.ndarray]:
    beat = np.full(length, -6.0)
    downbeat = np.full(length, -6.0)
    beat[np.arange(0, length, 25)] = 6.0
    downbeat[np.arange(0, length, 100)] = 6.0
    return beat, downbeat


def test_json_config_matches_python_default() -> None:
    path = Path(__file__).parents[1] / "config" / "casm-7f-default.json"
    payload = json.loads(path.read_text())
    assert CASMConfig.from_json(path).to_dict() == payload["parameters"]
    assert payload["calibration_folds"] == list(range(1, 8))


def test_regular_grid_and_downbeat_subset() -> None:
    beat, downbeat = regular_logits()
    beats, downbeats = CASMDecoder().decode(beat, downbeat)
    assert len(beats) >= 15
    assert np.all(np.diff(beats) > 0)
    assert all(np.any(np.isclose(beats, event)) for event in downbeats)


def test_probability_and_logit_inputs_are_equivalent() -> None:
    beat, downbeat = regular_logits()
    decoder = CASMDecoder()
    from_logits = decoder.decode(beat, downbeat)
    from_probabilities = decoder.decode(
        expit(beat), expit(downbeat), input_type="probabilities"
    )
    np.testing.assert_allclose(from_logits[0], from_probabilities[0])
    np.testing.assert_allclose(from_logits[1], from_probabilities[1])


def test_empty_and_invalid_inputs() -> None:
    decoder = CASMDecoder()
    beats, downbeats = decoder.decode([], [])
    assert beats.size == downbeats.size == 0
    with pytest.raises(ValueError, match="equal length"):
        decoder.decode([0.0], [0.0, 1.0])
    with pytest.raises(ValueError, match="one-dimensional"):
        decoder.decode([[0.0]], [[0.0]])
    with pytest.raises(ValueError, match="finite"):
        decoder.decode([np.nan], [0.0])


def test_cli_writes_reusable_npz(tmp_path: Path) -> None:
    beat, downbeat = regular_logits()
    source = tmp_path / "activations.npz"
    output = tmp_path / "events.npz"
    np.savez(source, beat_logits=beat, downbeat_logits=downbeat)
    assert main([str(source), "-o", str(output)]) == 0
    with np.load(output) as result:
        assert result["beats"].ndim == 1
        assert result["downbeats"].ndim == 1


def test_cli_writes_standard_beats_file(tmp_path: Path) -> None:
    beat, downbeat = regular_logits()
    source = tmp_path / "activations.npz"
    output = tmp_path / "events.beats"
    np.savez(source, beat_logits=beat, downbeat_logits=downbeat)
    main([str(source), "-o", str(output)])
    rows = [line.split("\t") for line in output.read_text().splitlines()]
    assert rows
    assert all(len(row) == 2 for row in rows)
    assert "1" in {row[1] for row in rows}


def test_beat_numbers_start_at_one_without_detected_downbeats() -> None:
    beats = np.asarray([0.1, 0.6, 1.1])
    np.testing.assert_array_equal(
        _infer_beat_numbers(beats, np.empty(0)), np.asarray([1, 2, 3])
    )


def test_seeded_release_regression() -> None:
    """Anchor the refactor to output checked against the sealed decoder."""
    rng = np.random.default_rng(20260921)
    beat = rng.normal(-3.0, 2.0, 311)
    downbeat = rng.normal(-4.0, 2.0, 311)
    beat[::18] += 7.0
    downbeat[::62] += 7.0
    beats, downbeats = CASMDecoder().decode(beat, downbeat)
    np.testing.assert_array_equal(
        beats,
        np.asarray(
            [
                0.0, 0.1, 0.2, 0.36, 0.56, 0.64, 0.72, 0.92, 1.0, 1.08,
                1.44, 1.66, 1.8, 1.94, 2.08, 2.56, 2.88, 3.14, 3.24,
                3.36, 3.6, 3.8, 3.96, 4.08, 4.32, 4.68, 5.04, 5.4,
                5.76, 6.12,
            ]
        ),
    )
    np.testing.assert_array_equal(
        downbeats,
        np.asarray([0.0, 1.08, 1.8, 2.56, 3.14, 3.8, 4.68, 5.04, 6.12]),
    )
