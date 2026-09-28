"""Frozen CASM configuration and JSON loading helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields, replace
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CASMConfig:
    """CASM parameters selected on the union of SMC folds 1--7.

    The defaults are the release configuration. Pass explicit overrides only
    for controlled ablations; normal inference should use ``CASMConfig()``.
    """

    fps: float = 50.0
    candidate_threshold: float = 0.03
    min_bpm: float = 30.0
    max_bpm: float = 300.0
    local_window_seconds: float = 8.0
    temperature: float = 2.0
    logit_clip: float = 6.0
    duration_weight: float = 4.0
    duration_sigma: float = 0.15
    uncertain_sigma: float = 0.4
    tempo_bias: float = 0.15
    fallback_minimal_ratio: float = 0.85
    fallback_maximal_ratio: float = 1.8
    downbeat_mode: str = "meter"
    meters: tuple[int, ...] = (2, 3, 4, 5, 6, 7)
    meter_change_penalty: float = 3.0
    downbeat_temperature: float = 4.0
    bar_reward: float = 0.0
    downbeat_agreement_threshold: float = 0.6
    downbeat_agreement_tolerance: float = 0.07

    def __post_init__(self) -> None:
        if self.fps <= 0:
            raise ValueError("fps must be positive")
        if not 0 < self.min_bpm < self.max_bpm:
            raise ValueError("expected 0 < min_bpm < max_bpm")
        if self.local_window_seconds <= 0:
            raise ValueError("local_window_seconds must be positive")
        if self.duration_sigma <= 0 or self.uncertain_sigma < 0:
            raise ValueError("duration sigmas must be non-negative and non-zero")
        if not self.meters or any(meter < 1 for meter in self.meters):
            raise ValueError("meters must contain positive integers")
        if self.downbeat_mode not in {"meter", "snap"}:
            raise ValueError("downbeat_mode must be 'meter' or 'snap'")

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "CASMConfig":
        known = {field.name for field in fields(cls)}
        unknown = sorted(set(values) - known)
        if unknown:
            raise ValueError(f"unknown CASM parameter(s): {', '.join(unknown)}")
        normalized = dict(values)
        if "meters" in normalized:
            normalized["meters"] = tuple(int(value) for value in normalized["meters"])
        return cls(**normalized)

    @classmethod
    def from_json(cls, path: str | Path) -> "CASMConfig":
        payload = json.loads(Path(path).read_text())
        if "parameters" in payload:
            payload = payload["parameters"]
        if not isinstance(payload, dict):
            raise ValueError("configuration JSON must contain an object")
        return cls.from_mapping(payload)

    def with_overrides(self, **values: Any) -> "CASMConfig":
        return replace(self, **values)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["meters"] = list(self.meters)
        return payload


DEFAULT_CONFIG = CASMConfig()
