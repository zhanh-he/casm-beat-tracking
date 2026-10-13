#!/usr/bin/env python3
"""Small dependency-free CASM throughput benchmark."""

from __future__ import annotations

import argparse
from time import perf_counter

import numpy as np

from casm_beat_tracking import CASMDecoder, CASMProcessor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=30.0)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument(
        "--api", choices=("processor", "decoder"), default="processor"
    )
    args = parser.parse_args()

    rng = np.random.default_rng(0)
    frames = int(args.minutes * 60 * 50)
    beat = rng.normal(-4.0, 0.5, frames)
    downbeat = rng.normal(-5.0, 0.5, frames)
    period = 25
    beat[np.arange(0, frames, period)] = 5.0
    downbeat[np.arange(0, frames, 4 * period)] = 5.0
    if args.api == "processor":
        processor = CASMProcessor(input_type="logits")
        activations = np.column_stack((beat, downbeat))

        def decode() -> np.ndarray:
            return processor(activations)

    else:
        decoder = CASMDecoder()

        def decode() -> tuple[np.ndarray, np.ndarray]:
            return decoder.decode(beat, downbeat)

    decode()
    elapsed = []
    for _ in range(args.repeats):
        start = perf_counter()
        decode()
        elapsed.append(perf_counter() - start)
    median = float(np.median(elapsed))
    print(f"API: {args.api}")
    print(f"audio: {args.minutes:.1f} min")
    print(f"median decode: {median:.4f} s")
    print(f"real-time factor: {median / (args.minutes * 60):.6f}")
    print(f"x real time: {args.minutes * 60 / median:.1f}")


if __name__ == "__main__":
    main()
