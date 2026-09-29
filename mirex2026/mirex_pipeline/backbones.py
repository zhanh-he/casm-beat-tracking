"""Manifest-driven audio frontend registry.

BeatThis and MSCNN share the audited Audio2Frames adapter in the project fork.
BeatFM intentionally remains a disabled manifest slot until its inference
source and final checkpoint are copied into this branch.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import json
from pathlib import Path
from typing import Any, Protocol

from .contracts import FrameActivations


class AudioBackbone(Protocol):
    def predict(self, audio_path: Path) -> FrameActivations: ...


@dataclass(frozen=True, slots=True)
class BackboneSpec:
    name: str
    status: str
    adapter: str | None
    checkpoint: str
    fps: float
    description: str


def load_specs(path: Path) -> dict[str, BackboneSpec]:
    payload = json.loads(path.read_text())
    entries = payload.get("backbones")
    if not isinstance(entries, dict):
        raise ValueError("backbone manifest must contain a 'backbones' object")
    specs: dict[str, BackboneSpec] = {}
    for name, values in entries.items():
        if not isinstance(values, dict):
            raise ValueError(f"invalid backbone entry: {name}")
        specs[name] = BackboneSpec(
            name=name,
            status=str(values["status"]),
            adapter=values.get("adapter"),
            checkpoint=str(values["checkpoint"]),
            fps=float(values.get("fps", 50.0)),
            description=str(values.get("description", "")),
        )
    return specs


def _load_class(dotted_path: str) -> type[Any]:
    try:
        module_name, class_name = dotted_path.split(":", 1)
    except ValueError as exc:
        raise ValueError(f"invalid adapter path: {dotted_path!r}") from exc
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def load_backbone(
    name: str,
    *,
    manifest_path: Path,
    checkpoint_override: Path | None,
    device: str,
) -> AudioBackbone:
    specs = load_specs(manifest_path)
    if name not in specs:
        raise ValueError(
            f"unknown backbone {name!r}; available: {', '.join(sorted(specs))}"
        )
    spec = specs[name]
    if spec.adapter is None:
        raise RuntimeError(
            f"backbone {name!r} is not wired yet (status={spec.status}). "
            "Add its audited adapter and checkpoint to config/backbones.json."
        )
    checkpoint = (
        checkpoint_override.resolve()
        if checkpoint_override is not None
        else (manifest_path.parent.parent / spec.checkpoint).resolve()
    )
    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"checkpoint for {name!r} is missing: {checkpoint}. "
            "Build the final bundle or pass --checkpoint."
        )
    adapter_class = _load_class(spec.adapter)
    return adapter_class(checkpoint=checkpoint, device=device, fps=spec.fps)
