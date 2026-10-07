"""Command-line interface for the MIREX 2026 inference matrix."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from .backbones import load_backbone, load_specs
from .decoders import make_decoder


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "config" / "backbones.json"
DEFAULT_CASM_CONFIG = ROOT / "config" / "casm-no-smc.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a MIREX backbone with Direct, DBN, or CASM decoding."
    )
    parser.add_argument("input", nargs="?", type=Path, help="single input WAV")
    parser.add_argument("output", nargs="?", type=Path, help="event-time text file")
    parser.add_argument("--backbone", default="beatthis")
    parser.add_argument(
        "--decoder", choices=("direct", "dbn", "dbn55_215", "dbn30_300", "casm"), default="casm"
    )
    parser.add_argument(
        "--task",
        choices=("beat", "downbeat"),
        default="beat",
        help="write beat or downbeat event times; default is beat",
    )
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--casm-config", type=Path, default=DEFAULT_CASM_CONFIG)
    dbn_group = parser.add_mutually_exclusive_group()
    dbn_group.add_argument(
        "--dbn-bpm",
        nargs=2,
        type=float,
        metavar=("MIN", "MAX"),
        help="DBN tempo range; default is 55 215",
    )
    dbn_group.add_argument(
        "--dbn-wide",
        action="store_true",
        help="exploratory alias for --dbn-bpm 30 300",
    )
    parser.add_argument(
        "--device", default=os.environ.get("MIREX_DEVICE", "auto")
    )
    parser.add_argument(
        "--list-backbones", action="store_true", help="print registry and exit"
    )
    return parser


def resolved_dbn_bpm(args: argparse.Namespace) -> tuple[float, float]:
    if getattr(args, "decoder", "dbn") == "dbn55_215":
        if args.dbn_wide or args.dbn_bpm is not None:
            raise ValueError("dbn55_215 does not accept DBN range overrides")
        return 55.0, 215.0
    if getattr(args, "decoder", "dbn") == "dbn30_300":
        if args.dbn_wide or args.dbn_bpm is not None:
            raise ValueError("dbn30_300 does not accept DBN range overrides")
        return 30.0, 300.0
    if args.dbn_wide and args.dbn_bpm is not None:
        raise ValueError("use either --dbn-wide or --dbn-bpm, not both")
    values = (30.0, 300.0) if args.dbn_wide else args.dbn_bpm
    minimum, maximum = (55.0, 215.0) if values is None else map(float, values)
    if not 0 < minimum < maximum:
        raise ValueError("DBN BPM range must satisfy 0 < MIN < MAX")
    return minimum, maximum


def _write_events(path: Path, events: np.ndarray, *, event_name: str) -> None:
    values = np.asarray(events, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise RuntimeError(f"decoder returned invalid {event_name} times")
    if np.any(np.diff(values) <= 0):
        raise RuntimeError(f"decoder returned non-increasing {event_name} times")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x") as handle:
        for value in values:
            handle.write(f"{value:.9f}\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list_backbones:
        payload = {
            name: {
                "status": spec.status,
                "checkpoint": spec.checkpoint,
                "fps": spec.fps,
                "description": spec.description,
            }
            for name, spec in load_specs(args.manifest).items()
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if args.input is None or args.output is None:
        parser.error("input and output are required unless --list-backbones is used")
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    if args.decoder == "casm" and not args.casm_config.is_file():
        raise FileNotFoundError(args.casm_config)

    backbone = load_backbone(
        args.backbone,
        manifest_path=args.manifest,
        checkpoint_override=args.checkpoint,
        device=args.device,
    )
    activations = backbone.predict(args.input)
    decoder = make_decoder(
        "dbn" if args.decoder.startswith("dbn") else args.decoder,
        casm_config=args.casm_config,
        dbn_bpm=resolved_dbn_bpm(args),
    )
    beats, downbeats = decoder.decode(activations)
    events = beats if args.task == "beat" else downbeats
    _write_events(args.output, events, event_name=args.task)


if __name__ == "__main__":
    main()
