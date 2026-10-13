#!/usr/bin/env python3
"""Add the two audited Figure 2b SMC cases to a demo site tree.

The script is intentionally site-root agnostic: run it against ``online-demo``
on the paper branch or ``docs`` on the GitHub Pages branch.  It preserves all
other cases, replaces any earlier SMC 001/032 records, embeds the resulting
payload in ``visualization.html``, and refreshes the integrity manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np


CASE_SPECS = {
    "smc_001_corrected.npz": {
        "id": "smc-001",
        "label": "SMC 001",
        "fold": "fold 2",
        "window_start": 15.5,
        "audio_file": "smc-001.mp3",
        "source_file": "SMC_001.wav",
        "summary": (
            "CASM removes Direct's local subdivision errors and follows the slow "
            "reference pulse; beat-only DBN selects the same pulse, whereas the "
            "released PLPDP path follows a faster competing subdivision."
        ),
    },
    "smc_032_corrected.npz": {
        "id": "smc-032",
        "label": "SMC 032",
        "fold": "fold 5",
        "window_start": 7.25,
        "audio_file": "smc-032.mp3",
        "source_file": "SMC_032.wav",
        "summary": (
            "The reference pulse accelerates from roughly 60 to 120 BPM. Direct, "
            "CASM, and released PLPDP follow the change, while beat-only DBN stays "
            "near the slower metrical level."
        ),
    },
}

CACHE_VERSION = "20261006-5"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--casm-manifest", type=Path, required=True)
    parser.add_argument("--source-figure", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rounded(values: np.ndarray, digits: int) -> list[float]:
    return np.round(np.asarray(values, dtype=float), digits).tolist()


def checked_events(values: np.ndarray, duration: float, name: str) -> list[float]:
    events = np.asarray(values, dtype=float)
    if np.any(np.diff(events) < 0):
        raise ValueError(f"{name} is not sorted")
    if np.any(events < 0) or np.any(events > duration + 1.0 / 50.0):
        raise ValueError(f"{name} contains an out-of-range event")
    return rounded(events, 4)


def metric_record(record: dict[str, object]) -> dict[str, float | int]:
    return {
        "fmeasure": round(float(record["fmeasure"]), 5),
        "cmlt": round(float(record["cmlt"]), 5),
        "amlt": round(float(record["amlt"]), 5),
        "event_count": int(record["event_count"]),
    }


def decoder_record(
    events: np.ndarray,
    metrics: dict[str, object],
    duration: float,
    name: str,
) -> dict[str, object]:
    beat_times = checked_events(events, duration, name)
    output = {
        "beat_times": beat_times,
        "downbeat_times": [],
        "beat_metrics": metric_record(metrics),
        "downbeat_metrics": None,
    }
    if output["beat_metrics"]["event_count"] != len(beat_times):
        raise ValueError(f"{name} event count disagrees with audit")
    return output


def build_case(
    trace_path: Path,
    spec: dict[str, object],
    audit: dict[str, object],
    casm_manifest: dict[str, object],
    site_root: Path,
) -> dict[str, object]:
    with np.load(trace_path, allow_pickle=False) as archive:
        trace = {key: archive[key] for key in archive.files}
    piece = str(trace["piece"].item())
    piece_audit = audit["pieces"][piece]
    fps = float(trace["fps"])
    duration = len(trace["beat_prob"]) / fps
    if fps != 50.0 or len(trace["beat_prob"]) != 2001:
        raise ValueError(f"unexpected trace geometry for {piece}")

    audio_path = site_root / "audio" / str(spec["audio_file"])
    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)
    audio_digest = sha256(audio_path)
    metrics = piece_audit["track_metrics"]
    candidates = np.asarray(trace["candidates"], dtype=float)
    periods = np.asarray(trace["periods"], dtype=float)
    confidence = np.asarray(trace["confidence"], dtype=float)
    if not (len(candidates) == len(periods) == len(confidence)):
        raise ValueError(f"CASM analysis arrays disagree for {piece}")

    dbn_audit = audit["dbn"]
    decoders = {
        "direct": decoder_record(trace["direct_beat"], metrics["direct"], duration, f"{piece}: Direct"),
        "casm": decoder_record(trace["casm_beat"], metrics["casm"], duration, f"{piece}: CASM"),
        "dbn": decoder_record(trace["dbn_beat_corrected"], metrics["dbn"], duration, f"{piece}: DBN"),
        "plpdp": decoder_record(
            trace["plpdp_beat"], metrics["plpdp"], duration, f"{piece}: PLPDP"
        ),
    }

    return {
        "id": spec["id"],
        "label": spec["label"],
        "screen_rank": None,
        "summary": spec["summary"],
        "public_audio": {
            "url": f"audio/{spec['audio_file']}?v={audio_digest[:12]}",
            "start_seconds": 0.0,
            "duration_seconds": 40.0,
            "source_file": spec["source_file"],
        },
        "data": {
            "piece": piece,
            "dataset": "smc",
            "front_end": "Beat This",
            "protocol": {
                "fold": spec["fold"],
                "role": "held-out test piece",
                "trim_seconds": 5.0,
                "semicrf_checkpoint_epoch": None,
            },
            "fps": fps,
            "duration_seconds": round(duration, 2),
            "window_seconds": 12.0,
            "beat_probability": rounded(trace["beat_prob"], 5),
            "downbeat_probability": [],
            "truth": {
                "beat_times": checked_events(trace["truth_beat"], duration, f"{piece}: GroundTruth"),
                "downbeat_times": [],
            },
            "decoders": decoders,
            "casm_analysis": {
                "candidate_times": rounded(candidates / fps, 4),
                "period_seconds": rounded(periods / fps, 4),
                "tempo_bpm": rounded(60.0 * fps / periods, 3),
                "reliability_proxy": rounded(confidence, 5),
                "local_window_seconds": float(casm_manifest["frozen_parameters"]["local_window_seconds"]),
                "provenance": "Frozen-7F CASM local period and reliability traces used in Figure 2b.",
            },
            "casm_configuration": {
                "label": "Frozen-7F",
                "parameters": casm_manifest["frozen_parameters"],
                "parameter_sha256": casm_manifest["frozen_parameter_sha256"],
            },
            "dbn_configuration": {
                "label": "beat-only DBN, matched 30–300 BPM range",
                "implementation": dbn_audit["implementation"],
                "input": dbn_audit["input"],
                "parameters": {
                    "min_bpm": dbn_audit["min_bpm"],
                    "max_bpm": dbn_audit["max_bpm"],
                    "num_tempi": dbn_audit["num_tempi"],
                    "transition_lambda": dbn_audit["transition_lambda"],
                    "observation_lambda": dbn_audit["observation_lambda"],
                    "threshold": dbn_audit["threshold"],
                },
                "correction_note": dbn_audit["note"],
            },
            "plpdp_configuration": {
                "label": "original Figure 2b PLPDP output",
                "correction_note": audit["plpdp"]["note"],
            },
            "recommended_window_start": spec["window_start"],
        },
    }


def main() -> None:
    args = parse_args()
    site_root = args.site_root.resolve()
    cases_path = site_root / "data" / "cases.json"
    visualization_path = site_root / "visualization.html"
    app_path = site_root / "app.js"
    index_path = site_root / "index.html"
    manifest_path = site_root / "data" / "manifest.json"

    audit = json.loads(args.audit.read_text())
    casm_manifest = json.loads(args.casm_manifest.read_text())
    cases = json.loads(cases_path.read_text())
    replacement_ids = {str(spec["id"]) for spec in CASE_SPECS.values()}
    cases = [case for case in cases if str(case["id"]) not in replacement_ids]
    additions = [
        build_case(args.data_dir / filename, spec, audit, casm_manifest, site_root)
        for filename, spec in CASE_SPECS.items()
    ]
    cases = additions + cases
    ids = [str(case["id"]) for case in cases]
    if len(ids) != len(set(ids)) or len(cases) != 8:
        raise ValueError(f"expected eight unique cases, got {ids}")

    compact = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    cases_path.write_text(compact + "\n")

    visualization = visualization_path.read_text()
    pattern = r"const CASES = .*?;\n    const DEMO = true;"
    replacement = f"const CASES = {compact};\n    const DEMO = true;"
    visualization, count = re.subn(pattern, replacement, visualization, count=1, flags=re.DOTALL)
    if count != 1:
        raise ValueError("could not locate the embedded CASES payload")
    visualization_path.write_text(visualization)

    app = re.sub(
        r'data/cases\.json\?v=[^"\']+',
        f"data/cases.json?v={CACHE_VERSION}",
        app_path.read_text(),
    )
    app_path.write_text(app)
    index = re.sub(r'app\.js\?v=[^"\']+', f"app.js?v={CACHE_VERSION}", index_path.read_text())
    index = re.sub(
        r'visualization\.html\?v=[^"\']+',
        f"visualization.html?v={CACHE_VERSION}",
        index,
    )
    index_path.write_text(index)

    manifest = json.loads(manifest_path.read_text())
    manifest["source_figure_generator"] = "archive/01-used/source/self-run-figures/figures-20260904-1443/fig02b-correction"
    manifest["source_figure_sha256"] = sha256(args.source_figure)
    manifest["case_data_sha256"] = sha256(cases_path)
    manifest["visualization_sha256"] = sha256(visualization_path)
    manifest["case_count"] = len(cases)
    manifest["audio_policy"] = (
        "Only the four selected SMC examples and four selected GTZAN examples are published; "
        "neither complete dataset is mirrored."
    )
    manifest["audio_files"] = {
        path.name: sha256(path) for path in sorted((site_root / "audio").glob("*.mp3"))
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps({"site_root": str(site_root), "case_ids": ids}, indent=2))


if __name__ == "__main__":
    main()
