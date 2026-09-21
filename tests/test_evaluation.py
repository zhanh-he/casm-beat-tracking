from __future__ import annotations

import math
from pathlib import Path

import pytest

from experiments.evaluate_activations import aggregate, infer_fold, json_safe


def test_fold_inference_is_explicit_and_unambiguous() -> None:
    assert infer_fold(Path("caches/fold0_val")) == 0
    assert infer_fold(Path("caches/beat_this_fold_7_val")) == 7
    assert infer_fold(Path("caches/final1_gtzan")) is None
    with pytest.raises(ValueError, match="ambiguous"):
        infer_fold(Path("caches/fold0/fold1_val"))


def test_aggregate_excludes_missing_downbeat_metrics() -> None:
    rows = [
        {
            "piece": "a",
            "dataset": "smc",
            "fold": 0,
            "beat_fmeasure": 0.5,
            "downbeat_fmeasure": math.nan,
        },
        {
            "piece": "b",
            "dataset": "ballroom",
            "fold": 1,
            "beat_fmeasure": 1.0,
            "downbeat_fmeasure": 0.75,
        },
    ]
    summary = aggregate(rows)
    assert summary["macro_piece"]["beat_fmeasure"] == 0.75
    assert summary["macro_piece"]["downbeat_fmeasure"] == 0.75
    assert set(summary["per_fold"]) == {"0", "1"}
    assert json_safe(summary["per_dataset"]["smc"])["downbeat_fmeasure"] == "nan"
