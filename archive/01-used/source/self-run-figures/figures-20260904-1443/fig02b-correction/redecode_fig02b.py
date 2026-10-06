#!/usr/bin/env python3
"""Re-decode only the DBN row in the two Figure 2b traces.

Run this script in the frozen ``auto-structbeat`` environment whose
``PYTHONPATH`` contains the archived ``structbeat`` checkout and its vendored
``third_party/plpdp4beat`` package.  The input trace already contains the exact
Beat This out-of-fold beat activation used by Direct and CASM, so no model
inference or private audio is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from structbeat.decoders import SequentialDBNDecoder
from structbeat.evaluation import beat_metrics


WINDOWS = {
    "smc/smc_001/track.npy": (15.5, 27.5),
    "smc/smc_032/track.npy": (7.25, 19.25),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_sha256(values: np.ndarray) -> str:
    """Hash an array's exact dtype, shape, and C-order bytes."""
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(json.dumps(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def local_f1(reference: np.ndarray, estimate: np.ndarray, tolerance: float = 0.07) -> float:
    reference = np.sort(np.asarray(reference, dtype=float))
    estimate = np.sort(np.asarray(estimate, dtype=float))
    i = j = matches = 0
    while i < len(reference) and j < len(estimate):
        delta = reference[i] - estimate[j]
        if abs(delta) <= tolerance:
            matches += 1
            i += 1
            j += 1
        elif delta < 0:
            i += 1
        else:
            j += 1
    denominator = len(reference) + len(estimate)
    return 0.0 if denominator == 0 else 2.0 * matches / denominator


def within(values: np.ndarray, start: float, end: float) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return values[(values >= start) & (values <= end)]


def metric_record(reference: np.ndarray, estimate: np.ndarray) -> dict[str, float | int]:
    values = beat_metrics(reference, estimate, trim_seconds=5.0)
    return {
        "fmeasure": float(values["fmeasure"]),
        "cmlt": float(values["cmlt"]),
        "amlt": float(values["amlt"]),
        "event_count": int(len(estimate)),
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit: dict[str, object] = {
        "status": "COMPLETE",
        "purpose": "Correct only the Figure 2b DBN visualization traces.",
        "shared_input": "Frozen Beat This OOF beat probability at 50 fps.",
        "unchanged_policy": (
            "Beat activation, reference, Direct, CASM, PLPDP, candidates, periods, "
            "and confidence are copied byte-for-byte from the original trace arrays."
        ),
        "dbn": {
            "implementation": "madmom.features.beats.DBNBeatTrackingProcessor via SequentialDBNDecoder",
            "input": "beat probability only",
            "fps": 50.0,
            "min_bpm": 30.0,
            "max_bpm": 300.0,
            "num_tempi": None,
            "transition_lambda": 100.0,
            "observation_lambda": 16,
            "threshold": 0.0,
            "correct": True,
            "note": "The old panel used the joint beat/downbeat DBN on beat-only SMC material.",
        },
        "plpdp": {
            "policy": "Preserved byte-for-byte from the original Figure 2b trace.",
            "note": "PLPDP is not re-decoded in this correction.",
        },
        "pieces": {},
    }

    dbn = SequentialDBNDecoder(fps=50.0, min_bpm=30.0, max_bpm=300.0)
    for trace_path in args.trace:
        with np.load(trace_path, allow_pickle=False) as archive:
            trace = {key: archive[key] for key in archive.files}
        piece = str(trace["piece"].item())
        if piece not in WINDOWS:
            raise ValueError(f"no audited window for {piece}")
        probability = np.asarray(trace["beat_prob"], dtype=np.float64)
        clipped = np.clip(probability, 1e-8, 1.0 - 1e-8)
        beat_logits = np.log(clipped / (1.0 - clipped))
        unused_downbeat_logits = np.full_like(beat_logits, -18.0)

        dbn_beats, _ = dbn.decode(beat_logits, unused_downbeat_logits)
        dbn_beats = np.asarray(dbn_beats, dtype=float)

        output_path = args.output_dir / f"{Path(piece).parts[1]}_corrected.npz"
        np.savez_compressed(
            output_path,
            **trace,
            dbn_beat_corrected=dbn_beats,
        )

        start, end = WINDOWS[piece]
        reference = np.asarray(trace["truth_beat"], dtype=float)
        window_reference = within(reference, start, end)
        methods = {
            "direct": np.asarray(trace["direct_beat"], dtype=float),
            "casm": np.asarray(trace["casm_beat"], dtype=float),
            "dbn": dbn_beats,
            "plpdp": np.asarray(trace["plpdp_beat"], dtype=float),
        }
        unchanged_keys = (
            "beat_prob",
            "truth_beat",
            "direct_beat",
            "casm_beat",
            "plpdp_beat",
            "candidates",
            "periods",
            "confidence",
        )
        audit["pieces"][piece] = {
            "source_trace": trace_path.name,
            "source_trace_sha256": sha256(trace_path),
            "corrected_trace": output_path.name,
            "corrected_trace_sha256": sha256(output_path),
            "unchanged_array_sha256": {
                key: array_sha256(np.asarray(trace[key])) for key in unchanged_keys
            },
            "window_seconds": [start, end],
            "track_metrics": {
                name: metric_record(reference, events)
                for name, events in methods.items()
            },
            "window_f1": {
                name: local_f1(window_reference, within(events, start, end))
                for name, events in methods.items()
            },
            "window_event_count": {
                name: int(len(within(events, start, end)))
                for name, events in methods.items()
            },
        }

    audit_path = args.output_dir / "audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(audit_path)


if __name__ == "__main__":
    main()
