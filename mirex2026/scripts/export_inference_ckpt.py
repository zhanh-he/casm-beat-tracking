#!/usr/bin/env python3
"""Strip Lightning trainer state from one frozen MIREX checkpoint.

The export keeps FP32 model tensors and the architecture hyperparameters used
by the BeatThis/MSCNN/TCN inference adapters. It never quantizes weights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch


ARCHITECTURES = {
    "beatthis": "beat_this",
    "mscnn": "multiscale_cnn",
    "tcn": "tcn",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=ARCHITECTURES, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--epoch", type=int, required=True)
    args = parser.parse_args()

    source = args.input.resolve(strict=True)
    destination = args.output.resolve()
    if destination.exists():
        parser.error(f"refusing to overwrite {destination}")
    source_hash = sha256(source)
    if source_hash != args.expected_source_sha256:
        raise ValueError(f"source SHA-256 mismatch: {source_hash}")

    original = torch.load(source, map_location="cpu", weights_only=False)
    params = original["hyper_parameters"]
    architecture = params.get("architecture", "beat_this")
    if architecture != ARCHITECTURES[args.model]:
        raise ValueError(f"unexpected architecture {architecture!r}")
    state = original["state_dict"]
    if not state or any(not key.startswith("model.") for key in state):
        raise ValueError("expected an inference-only model.* state_dict")
    if any(not isinstance(tensor, torch.Tensor) for tensor in state.values()):
        raise ValueError("state_dict contains a non-tensor value")
    if int(original["epoch"]) != args.epoch:
        raise ValueError(f"checkpoint epoch {original['epoch']} differs from requested epoch")

    exported = {
        "hyper_parameters": params,
        "state_dict": {key: value.detach().cpu().contiguous() for key, value in state.items()},
        "epoch": args.epoch,
        "mirex_export": {
            "schema_version": 1,
            "model": args.model,
            "seed": args.seed,
            "zero_based_epoch": args.epoch,
            "source_sha256": source_hash,
            "training_protocol": "MIREX 2026 no-SMC/no-GTZAN allowed-validation-selected split weight",
            "precision": "original tensor dtypes; no quantization",
            "removed": "optimizer, scheduler, trainer loops, callbacks, datamodule state",
        },
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    torch.save(exported, destination)
    # Ensure the exported artifact is loadable by PyTorch's restricted loader.
    loaded = torch.load(destination, map_location="cpu", weights_only=True)
    if set(loaded["state_dict"]) != set(state):
        raise RuntimeError("export lost model keys")
    if any(not torch.equal(loaded["state_dict"][key], value) for key, value in state.items()):
        raise RuntimeError("export changed a model tensor")
    print(json.dumps({
        "model": args.model,
        "input_bytes": source.stat().st_size,
        "output_bytes": destination.stat().st_size,
        "source_sha256": source_hash,
        "output_sha256": sha256(destination),
        "model_tensor_count": len(state),
        "tensors_bitwise_identical": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
