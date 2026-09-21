"""Command-line interface for decoding saved framewise activations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import numpy as np

from .config import CASMConfig
from .decoder import CASMDecoder


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="casm-decode",
        description="Decode beat/downbeat activation arrays with CASM 7F.",
    )
    parser.add_argument("input", type=Path, help="input .npz activation file")
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--config", type=Path, help="optional CASM JSON config")
    parser.add_argument("--beat-key", default="beat_logits")
    parser.add_argument("--downbeat-key", default="downbeat_logits")
    parser.add_argument(
        "--input-type", choices=("logits", "probabilities"), default="logits"
    )
    return parser


def _infer_beat_numbers(beats: np.ndarray, downbeats: np.ndarray) -> np.ndarray:
    downbeat_indices = [
        index
        for index, beat in enumerate(beats)
        if np.any(np.isclose(downbeats, beat, atol=1e-9))
    ]
    if len(downbeat_indices) >= 2:
        meter = downbeat_indices[1] - downbeat_indices[0]
        pickup = downbeat_indices[0]
        counter = meter - pickup if pickup < meter else 1
    else:
        counter = 0
    numbers: list[int] = []
    downbeat_set = set(downbeat_indices)
    for index in range(len(beats)):
        if index in downbeat_set:
            counter = 1
        else:
            counter += 1
        numbers.append(counter)
    return np.asarray(numbers, dtype=np.int64)


def _write_tsv(path: Path, beats: np.ndarray, downbeats: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    numbers = _infer_beat_numbers(beats, downbeats)
    with path.open("w") as handle:
        for beat, number in zip(beats, numbers):
            handle.write(f"{beat:.9f}\t{number}\n")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = CASMConfig.from_json(args.config) if args.config else CASMConfig()
    with np.load(args.input) as payload:
        missing = [
            key
            for key in (args.beat_key, args.downbeat_key)
            if key not in payload
        ]
        if missing:
            raise SystemExit(f"missing input key(s): {', '.join(missing)}")
        beats, downbeats = CASMDecoder(config).decode(
            payload[args.beat_key],
            payload[args.downbeat_key],
            input_type=args.input_type,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".npz":
        np.savez_compressed(args.output, beats=beats, downbeats=downbeats)
    elif args.output.suffix.lower() in {".tsv", ".txt", ".beats"}:
        _write_tsv(args.output, beats, downbeats)
    else:
        raise SystemExit("output must end in .npz, .tsv, .txt, or .beats")
    print(f"decoded {len(beats)} beats and {len(downbeats)} downbeats")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
