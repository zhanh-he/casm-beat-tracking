"""Command-line interface for decoding saved framewise activations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import numpy as np

from . import __version__
from .config import CASMConfig
from .decoder import CASMDecoder
from .processors import beat_numbers


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="casm-decode",
        description="Decode beat/downbeat activation arrays with CASM 7F.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="input .npz with separate arrays or .npy with shape (frames, 2)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--config", type=Path, help="optional CASM JSON config")
    parser.add_argument("--beat-key", default="beat_logits")
    parser.add_argument("--downbeat-key", default="downbeat_logits")
    parser.add_argument(
        "--input-type", choices=("logits", "probabilities"), default="logits"
    )
    return parser


def _load_activations(
    path: Path, beat_key: str, downbeat_key: str
) -> tuple[np.ndarray, np.ndarray]:
    if path.suffix.lower() == ".npy":
        values = np.load(path, allow_pickle=False)
        if values.ndim != 2 or values.shape[1] != 2:
            raise SystemExit(".npy input must have shape (frames, 2)")
        return values[:, 0], values[:, 1]
    if path.suffix.lower() != ".npz":
        raise SystemExit("input must end in .npz or .npy")

    with np.load(path, allow_pickle=False) as payload:
        missing = [key for key in (beat_key, downbeat_key) if key not in payload]
        if missing:
            raise SystemExit(f"missing input key(s): {', '.join(missing)}")
        return payload[beat_key].copy(), payload[downbeat_key].copy()


def _infer_beat_numbers(beats: np.ndarray, downbeats: np.ndarray) -> np.ndarray:
    """Backward-compatible wrapper around the public numbering helper."""
    return beat_numbers(beats, downbeats)


def _write_tsv(path: Path, beats: np.ndarray, downbeats: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    numbers = _infer_beat_numbers(beats, downbeats)
    with path.open("w") as handle:
        for beat, number in zip(beats, numbers):
            handle.write(f"{beat:.9f}\t{number}\n")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = CASMConfig.from_json(args.config) if args.config else CASMConfig()
    beat_values, downbeat_values = _load_activations(
        args.input, args.beat_key, args.downbeat_key
    )
    beats, downbeats = CASMDecoder(config).decode(
        beat_values,
        downbeat_values,
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
