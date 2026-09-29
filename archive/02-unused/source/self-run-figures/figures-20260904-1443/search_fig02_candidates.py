#!/usr/bin/env python3
"""Mine auditable Frozen-7F candidates for the Figure 2 mechanism pair.

The historical representative selector optimized CASM only against Direct and
therefore could choose a window in which DBN or PLPDP was visibly better. This
script re-decodes every requested cache with the exact locked Frozen-7F
parameters, scans every 12-second window, and requires a clear-periodicity
candidate to beat Direct, both DBN settings, and PLPDP.

For the ambiguity panel, CASM and Direct must emit the exact same events in the
window, the local period margin must be low, and no safeguard fallback may have
occurred. The shortlist is explicitly post hoc visual evidence and must not be
presented as an aggregate performance estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import expit

from run_mechanism_ablation import (
    CASMDecoder,
    MinimalDecoder,
    _edge_local_maxima,
    canonical_json,
    casm_trace,
    load_cache_item,
    make_decoder,
    normalized_frozen,
    sha256_file,
)


METRICS = ("beat_fmeasure", "beat_cmlt", "beat_amlt")
CLEAR_COMPARATORS = ("direct", "dbn_default", "dbn_matched_30_300", "plpdp")
TRACE_KEYS = {
    "direct": "direct_beat",
    "casm_full": "casm_beat",
    "dbn_default": "dbn_default_beat",
    "dbn_matched_30_300": "dbn_matched_beat",
    "plpdp": "plpdp_beat",
}

_FROZEN: dict[str, object] | None = None
_TRACE_DIR: Path | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--frozen-lock", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panels", nargs="+", default=["bt_smc_oof"])
    parser.add_argument("--family", default="exhaustive_7f")
    parser.add_argument("--top-clear", type=int, default=16)
    parser.add_argument("--top-ambiguous", type=int, default=16)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--window-seconds", type=float, default=12.0)
    parser.add_argument("--window-step", type=float, default=0.25)
    parser.add_argument("--trim-seconds", type=float, default=5.0)
    parser.add_argument(
        "--keep-all-traces",
        action="store_true",
        help="retain traces for all source pieces instead of shortlisted pieces only",
    )
    return parser.parse_args()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def load_frozen(lock_path: Path, family: str) -> tuple[dict[str, object], dict[str, object]]:
    lock = json.loads(lock_path.read_text())
    configurations = lock.get("payload", lock).get("configurations", [])
    matches = [row for row in configurations if row.get("family") == family]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {family!r} configuration, found {len(matches)}")
    selected = matches[0]
    frozen = dict(selected["selected_parameters"])
    parameter_hash = hashlib.sha256(canonical_json(frozen).encode()).hexdigest()
    expected_candidate_hash = str(selected["selected_candidate_hash"])
    if parameter_hash != expected_candidate_hash:
        raise RuntimeError(
            f"selected parameter hash mismatch: {parameter_hash} != {expected_candidate_hash}"
        )
    return frozen, selected


def source_table(data_dir: Path, panels: list[str]) -> pd.DataFrame:
    mechanism = pd.read_csv(data_dir / "mechanism_piece_summary.csv")
    mechanism = mechanism.loc[
        mechanism.panel.isin(panels), ["panel", "piece", "source_path"]
    ].copy()
    duplicates = mechanism.duplicated(["panel", "piece"], keep=False)
    if duplicates.any():
        raise RuntimeError("duplicate panel/piece rows in mechanism source table")
    missing = [path for path in mechanism.source_path if not Path(str(path)).exists()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} cache paths are missing; first: {missing[0]}")
    return mechanism.sort_values(["panel", "piece"]).reset_index(drop=True)


def baseline_table(data_dir: Path, panels: list[str]) -> pd.DataFrame:
    tables: list[pd.DataFrame] = []
    for panel in panels:
        merged: pd.DataFrame | None = None
        for method in CLEAR_COMPARATORS:
            path = data_dir / "raw" / f"{panel}__{method}.pieces.csv"
            table = pd.read_csv(path)[["piece", *METRICS]].copy()
            table.insert(0, "panel", panel)
            table = table.rename(
                columns={metric: f"{method}__{metric}" for metric in METRICS}
            )
            merged = table if merged is None else merged.merge(
                table, on=["panel", "piece"], validate="one_to_one"
            )
        assert merged is not None
        tables.append(merged)
    return pd.concat(tables, ignore_index=True)


def piece_slug(panel: str, piece: str) -> str:
    stem = piece.removesuffix("/track.npy").replace("/", "__")
    return f"{panel}__{stem}"


def init_worker(frozen: dict[str, object], trace_dir: str) -> None:
    global _FROZEN, _TRACE_DIR
    _FROZEN = frozen
    _TRACE_DIR = Path(trace_dir)


def analyse_piece(row: dict[str, str]) -> dict[str, object]:
    """Recompute CASM under Frozen-7F and export every comparator trace."""
    if _FROZEN is None or _TRACE_DIR is None:
        raise RuntimeError("worker was not initialized")
    path = Path(row["source_path"])
    summary, _, _ = casm_trace(path, _FROZEN)
    item = load_cache_item(path)
    decoder = CASMDecoder(**normalized_frozen(_FROZEN))
    logits = np.asarray(item["beat_logits"], dtype=float)
    probabilities = expit(logits)
    candidates = _edge_local_maxima(probabilities)
    candidates = candidates[probabilities[candidates] >= decoder.candidate_threshold]
    periods, confidence = decoder._estimate_local_tempo(probabilities, candidates)

    decoded: dict[str, np.ndarray] = {}
    for method in TRACE_KEYS:
        method_decoder = (
            decoder
            if method == "casm_full"
            else MinimalDecoder(fps=decoder.fps)
            if method == "direct"
            else make_decoder(method, _FROZEN)
        )
        beats, _ = method_decoder.decode(item["beat_logits"], item["downbeat_logits"])
        decoded[method] = np.asarray(beats, dtype=float)
        if method in ("dbn_default", "dbn_matched_30_300", "plpdp") and not len(beats):
            raise RuntimeError(f"{method} returned no beat events for {row['piece']}")

    trace_name = piece_slug(row["panel"], row["piece"]) + ".npz"
    np.savez_compressed(
        _TRACE_DIR / trace_name,
        piece=np.asarray(item["piece"]),
        panel=np.asarray(row["panel"]),
        fps=np.asarray(decoder.fps),
        beat_prob=probabilities,
        truth_beat=np.asarray(item["truth_beat"], dtype=float),
        candidates=candidates,
        periods=periods,
        confidence=confidence,
        direct_beat=decoded["direct"],
        casm_beat=decoded["casm_full"],
        dbn_default_beat=decoded["dbn_default"],
        dbn_matched_beat=decoded["dbn_matched_30_300"],
        plpdp_beat=decoded["plpdp"],
    )
    return {
        **summary,
        "panel": row["panel"],
        "piece": row["piece"],
        "source_path": row["source_path"],
        "trace_file": trace_name,
    }


def event_matches(reference: np.ndarray, estimate: np.ndarray, tolerance: float = 0.07) -> int:
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
    return matches


def local_f1(reference: np.ndarray, estimate: np.ndarray) -> float:
    denominator = len(reference) + len(estimate)
    return 0.0 if denominator == 0 else 2.0 * event_matches(reference, estimate) / denominator


def within(values: np.ndarray, start: float, end: float) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return values[(values >= start) & (values <= end)]


def exact_events(first: np.ndarray, second: np.ndarray) -> bool:
    return len(first) == len(second) and bool(
        np.allclose(first, second, rtol=0.0, atol=1e-10)
    )


def scan_windows(
    trace_path: Path,
    width: float,
    step: float,
    trim: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    with np.load(trace_path, allow_pickle=False) as archive:
        trace = {key: archive[key] for key in archive.files}
    fps = float(trace["fps"])
    duration = len(trace["beat_prob"]) / fps
    last_start = duration - trim - width
    if last_start >= trim:
        starts = np.arange(trim, last_start + 1e-9, step)
    else:
        starts = np.asarray([max(0.0, 0.5 * (duration - width))])
        width = min(width, duration)
    candidate_times = trace["candidates"] / fps
    clear_rows: list[dict[str, object]] = []
    ambiguous_rows: list[dict[str, object]] = []
    for raw_start in starts:
        start = float(raw_start)
        end = min(float(start + width), duration)
        truth = within(trace["truth_beat"], start, end)
        if len(truth) < 6:
            continue
        method_events = {
            method: within(trace[key], start, end)
            for method, key in TRACE_KEYS.items()
        }
        method_f1 = {
            method: local_f1(truth, events) for method, events in method_events.items()
        }
        mask = (candidate_times >= start) & (candidate_times <= end)
        margin = np.asarray(trace["confidence"])[mask]
        if not len(margin):
            continue
        common: dict[str, Any] = {
            "start": start,
            "end": end,
            "truth_count": int(len(truth)),
            "method_f1": {key: float(value) for key, value in method_f1.items()},
            "method_count": {
                key: int(len(value)) for key, value in method_events.items()
            },
            "margin_mean": float(np.mean(margin)),
            "margin_median": float(np.median(margin)),
            "margin_max": float(np.max(margin)),
            "casm_direct_exact": exact_events(
                method_events["casm_full"], method_events["direct"]
            ),
        }

        casm = method_f1["casm_full"]
        clear_gaps = [casm - method_f1[method] for method in CLEAR_COMPARATORS]
        if casm >= 0.55 and min(clear_gaps) >= 0.025:
            common_clear = dict(common)
            common_clear["min_f1_gain"] = float(min(clear_gaps))
            common_clear["mean_f1_gain"] = float(np.mean(clear_gaps))
            common_clear["score"] = float(
                4.0 * min(clear_gaps)
                + np.mean(clear_gaps)
                + 0.5 * casm
                + 0.30 * common["margin_mean"]
                + 0.01 * min(len(truth), 12)
            )
            clear_rows.append(common_clear)

        structured_gaps = [
            casm - method_f1[method]
            for method in ("dbn_default", "dbn_matched_30_300", "plpdp")
        ]
        if (
            common["casm_direct_exact"]
            and common["margin_mean"] <= 0.16
            and common["margin_median"] <= 0.16
            and casm >= 0.35
            and min(structured_gaps) >= -0.01
        ):
            common_ambiguous = dict(common)
            common_ambiguous["min_structured_f1_gain"] = float(min(structured_gaps))
            common_ambiguous["mean_structured_f1_gain"] = float(np.mean(structured_gaps))
            common_ambiguous["score"] = float(
                2.5 * min(structured_gaps)
                + np.mean(structured_gaps)
                + 0.35 * casm
                - 1.2 * common["margin_mean"]
                - 0.25 * common["margin_max"]
                + 0.01 * min(len(truth), 12)
            )
            ambiguous_rows.append(common_ambiguous)
    return clear_rows, ambiguous_rows


def track_metrics(row: pd.Series) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for method in ("casm_full", *CLEAR_COMPARATORS):
        result[method] = {
            metric: float(row[f"{method}__{metric}"]) for metric in METRICS
        }
    return result


def best_by_piece(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    best: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        key = (str(row["panel"]), str(row["piece"]))
        if key not in best or float(row["window"]["score"]) > float(best[key]["window"]["score"]):
            best[key] = row
    return sorted(best.values(), key=lambda row: float(row["window"]["score"]), reverse=True)


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    lock_path = args.frozen_lock.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_dir}")
    trace_dir = output_dir / "traces"
    trace_dir.mkdir(parents=True)

    frozen, selected = load_frozen(lock_path, args.family)
    sources = source_table(data_dir, args.panels)
    baselines = baseline_table(data_dir, args.panels)
    input_rows = sources.astype(str).to_dict("records")
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=init_worker,
        initargs=(frozen, str(trace_dir)),
    ) as executor:
        summaries = list(executor.map(analyse_piece, input_rows, chunksize=2))

    summary_table = pd.DataFrame(summaries)
    summary_table.to_csv(output_dir / "frozen_7f_casm_piece_summary.csv", index=False)
    casm_metrics = summary_table[
        [
            "panel",
            "piece",
            "trace_file",
            "source_path",
            "beat_fallback",
            "count_ratio",
            "period_margin_mean",
            "period_margin_median",
            *[f"casm_beat_{suffix}" for suffix in ("fmeasure", "cmlt", "amlt")],
        ]
    ].rename(
        columns={
            "casm_beat_fmeasure": "casm_full__beat_fmeasure",
            "casm_beat_cmlt": "casm_full__beat_cmlt",
            "casm_beat_amlt": "casm_full__beat_amlt",
        }
    )
    joined = casm_metrics.merge(baselines, on=["panel", "piece"], validate="one_to_one")

    all_clear: list[dict[str, object]] = []
    all_ambiguous: list[dict[str, object]] = []
    for _, row in joined.iterrows():
        if bool(row.beat_fallback):
            continue
        clear_windows, ambiguous_windows = scan_windows(
            trace_dir / str(row.trace_file),
            args.window_seconds,
            args.window_step,
            args.trim_seconds,
        )
        base = {
            "panel": str(row.panel),
            "piece": str(row.piece),
            "source_path": str(row.source_path),
            "trace_file": str(row.trace_file),
            "beat_fallback": False,
            "count_ratio": float(row.count_ratio),
            "period_margin_mean": float(row.period_margin_mean),
            "period_margin_median": float(row.period_margin_median),
            "track_metrics": track_metrics(row),
        }
        for window in clear_windows:
            all_clear.append({**base, "role": "clear", "window": window})
        for window in ambiguous_windows:
            all_ambiguous.append({**base, "role": "ambiguous", "window": window})

    clear = best_by_piece(all_clear)[: args.top_clear]
    ambiguous = best_by_piece(all_ambiguous)[: args.top_ambiguous]
    for role_rows in (clear, ambiguous):
        for rank, row in enumerate(role_rows, 1):
            row["rank"] = rank
    records = clear + ambiguous
    if not clear or not ambiguous:
        raise RuntimeError(
            f"insufficient candidates: clear={len(clear)}, ambiguous={len(ambiguous)}"
        )

    retained_traces = {str(record["trace_file"]) for record in records}
    if not args.keep_all_traces:
        for trace_path in trace_dir.glob("*.npz"):
            if trace_path.name not in retained_traces:
                trace_path.unlink()

    audit_rows: list[dict[str, object]] = []
    for record in records:
        window = record["window"]
        audit: dict[str, object] = {
            "role": record["role"],
            "rank": record["rank"],
            "panel": record["panel"],
            "piece": record["piece"],
            "window_start": window["start"],
            "window_end": window["end"],
            "window_margin_mean": window["margin_mean"],
            "window_margin_median": window["margin_median"],
            "casm_direct_exact": window["casm_direct_exact"],
        }
        for method in ("casm_full", *CLEAR_COMPARATORS):
            audit[f"window_f1__{method}"] = window["method_f1"][method]
            audit[f"window_count__{method}"] = window["method_count"][method]
            audit[f"track_f1__{method}"] = record["track_metrics"][method]["beat_fmeasure"]
        audit_rows.append(audit)
    pd.DataFrame(audit_rows).to_csv(output_dir / "candidate_audit.csv", index=False)

    manifest = {
        "status": "COMPLETE",
        "selection_is_post_hoc": True,
        "intended_use": "mechanism visualization only; not aggregate performance evidence",
        "selection_policy": {
            "clear": (
                "non-fallback; at least six references; window CASM F1 >= 0.55 and >= 0.025 "
                "above Direct, DBN default, DBN 30-300, and PLPDP"
            ),
            "ambiguous": (
                "non-fallback; exact CASM/Direct event equality in the window; mean and median "
                "period margin <= 0.16; CASM F1 >= 0.35; no more than 0.01 below either DBN or PLPDP"
            ),
        },
        "frozen_family": args.family,
        "configuration_hash": selected["configuration_hash"],
        "selected_candidate_hash": selected["selected_candidate_hash"],
        "frozen_parameter_sha256": hashlib.sha256(canonical_json(frozen).encode()).hexdigest(),
        "frozen_parameters": frozen,
        "frozen_lock": str(lock_path),
        "frozen_lock_sha256": sha256_file(lock_path),
        "baseline_reuse": (
            "Direct, DBN, and PLPDP whole-track metrics are reused from the mechanism bundle because "
            "they do not depend on CASM duration_sigma; every displayed event trace was decoded again."
        ),
        "panels": args.panels,
        "source_piece_count": int(len(sources)),
        "retained_trace_count": len(retained_traces),
        "window_seconds": args.window_seconds,
        "window_step": args.window_step,
        "trim_seconds": args.trim_seconds,
        "records": records,
    }
    write_json(output_dir / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": "COMPLETE",
                "source_pieces": len(sources),
                "clear_candidates": len(clear),
                "ambiguous_candidates": len(ambiguous),
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
