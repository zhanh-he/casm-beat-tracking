#!/usr/bin/env python3
"""Render auditable Figure 2 pair candidates from the multi-baseline search."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from plot_mechanism_evidence import (
    BLUE,
    BLUE_LIGHT,
    CHARCOAL,
    GREY,
    HEAT_RED,
    LIGHT_GREY,
    ORANGE,
    load_trace,
    plot_event_raster,
    save_all,
    setup_style,
)


PANEL_LABEL = {
    "bt_smc_oof": "Beat This / SMC OOF",
    "mscnn_smc_oof": "MSCNN / SMC OOF",
}
METHOD_ORDER = ("casm_full", "direct", "dbn_matched_30_300", "plpdp")
METHOD_SHORT = {
    "casm_full": "CASM",
    "direct": "Direct",
    "dbn_matched_30_300": "DBN",
    "plpdp": "PLPDP",
}
TRACE_METHODS = {
    "casm_full": "casm_beat",
    "direct": "direct_beat",
    "dbn_matched_30_300": "dbn_matched_beat",
    "plpdp": "plpdp_beat",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-dir", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    return parser.parse_args()


def find_record(
    records: list[dict[str, object]], panel: str, role: str, piece: str
) -> dict[str, object]:
    matches = [
        row
        for row in records
        if row["panel"] == panel and row["role"] == role and row["piece"] == piece
    ]
    if len(matches) != 1:
        raise RuntimeError((panel, role, piece, len(matches)))
    return matches[0]


def coefficient(confidence: np.ndarray, frozen: dict[str, object]) -> np.ndarray:
    sigma0 = float(frozen["duration_sigma"])
    sigmau = float(frozen["uncertain_sigma"])
    lam = float(frozen["duration_weight"])
    return lam * confidence / (2 * (sigma0 + (1 - confidence) * sigmau) ** 2)


def format_f1(values: dict[str, float]) -> str:
    return "  ".join(
        f"{METHOD_SHORT[method]} {float(values[method]):.2f}"
        for method in METHOD_ORDER
    )


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


def window_metrics(trace: dict[str, np.ndarray], start: float, end: float) -> dict[str, object]:
    truth = trace["truth_beat"]
    truth = truth[(truth >= start) & (truth <= end)]
    method_events = {
        method: trace[key][(trace[key] >= start) & (trace[key] <= end)]
        for method, key in TRACE_METHODS.items()
    }
    candidate_times = trace["candidates"] / float(trace["fps"])
    mask = (candidate_times >= start) & (candidate_times <= end)
    margins = trace["confidence"][mask]
    return {
        "start": start,
        "end": end,
        "truth_count": int(len(truth)),
        "method_f1": {
            method: local_f1(truth, events) for method, events in method_events.items()
        },
        "method_count": {
            method: int(len(events)) for method, events in method_events.items()
        },
        "margin_mean": float(np.mean(margins)),
        "margin_median": float(np.median(margins)),
        "margin_max": float(np.max(margins)),
        "casm_direct_exact": bool(
            np.array_equal(method_events["casm_full"], method_events["direct"])
        ),
    }


def render_pair(
    search_dir: Path,
    figure_dir: Path,
    pair: dict[str, object],
    clear: dict[str, object],
    ambiguous: dict[str, object],
    frozen: dict[str, object],
) -> dict[str, object]:
    fig, axes = plt.subplots(
        3,
        2,
        figsize=(7.15, 5.0),
        gridspec_kw={"height_ratios": [1.4, 1.0, 0.9]},
    )
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.88, bottom=0.24)
    roles = (
        ("clear", "(a) Clear periodicity: CASM wins across decoders", clear),
        ("ambiguous", "(b) Ambiguous evidence: CASM defers", ambiguous),
    )
    summary: dict[str, object] = {"id": pair["id"], "panel": pair["panel"], "columns": {}}
    for column, (role, heading, record) in enumerate(roles):
        trace = load_trace(search_dir / "traces" / str(record["trace_file"]))
        override = pair.get(f"{role}_window")
        window = (
            window_metrics(trace, float(override[0]), float(override[1]))
            if override is not None
            else record["window"]
        )
        start = float(window["start"])
        end = float(window["end"])
        fps = float(trace["fps"])
        frame_start = max(0, int(math.floor(start * fps)))
        frame_end = min(len(trace["beat_prob"]), int(math.ceil(end * fps)) + 1)
        times = np.arange(frame_start, frame_end) / fps

        ax = axes[0, column]
        ax.fill_between(
            times,
            trace["beat_prob"][frame_start:frame_end],
            color=LIGHT_GREY,
            alpha=0.65,
            lw=0,
        )
        ax.plot(times, trace["beat_prob"][frame_start:frame_end], color=GREY, lw=0.75)
        result_y = [-0.05, -0.16, -0.27, -0.38, -0.49]
        plot_event_raster(ax, trace["truth_beat"], result_y[0], CHARCOAL, "o", "Reference", start, end, size=12, linewidth=1.1)
        plot_event_raster(ax, trace["direct_beat"], result_y[1], BLUE, "|", "Direct", start, end, size=16, linewidth=1.1)
        plot_event_raster(ax, trace["casm_beat"], result_y[2], ORANGE, "x", "CASM", start, end, size=16, linewidth=1.1)
        plot_event_raster(ax, trace["dbn_matched_beat"], result_y[3], GREY, "^", "DBN (30–300 BPM)", start, end, size=16, linewidth=0.8)
        plot_event_raster(ax, trace["plpdp_beat"], result_y[4], HEAT_RED, "o", "PLPDP", start, end, size=16, linewidth=1.1, hollow=True)
        ax.set_xlim(start, end)
        ax.set_ylim(-0.54, 1.03)
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_ylabel("Beat activation" if column == 0 else "")
        short_piece = str(record["piece"]).removesuffix("/track.npy")
        ax.set_title(
            f"{heading}\n{PANEL_LABEL[str(pair['panel'])]} · {short_piece}",
            fontsize=8.0,
            fontweight="bold",
            pad=7,
        )
        ax.grid(axis="y")

        ax = axes[1, column]
        candidate_times = trace["candidates"] / fps
        mask = (candidate_times >= start) & (candidate_times <= end)
        target_bpm = 60.0 * fps / trace["periods"]
        ax.scatter(
            candidate_times[mask],
            target_bpm[mask],
            color=ORANGE,
            s=16,
            marker="x",
            linewidths=1.0,
            label="CASM local target",
        )
        truth = trace["truth_beat"]
        truth_bpm = 60.0 / np.diff(truth)
        truth_times = 0.5 * (truth[:-1] + truth[1:])
        truth_mask = (truth_times >= start) & (truth_times <= end)
        ax.plot(
            truth_times[truth_mask],
            truth_bpm[truth_mask],
            color=CHARCOAL,
            lw=1.1,
            marker="o",
            ms=2.8,
            label="Reference IBI",
        )
        ax.set_yscale("log")
        ax.set_ylim(28, 310)
        tempo_ticks = [30, 60, 120, 240, 300]
        ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(tempo_ticks))
        ax.yaxis.set_major_formatter(mpl.ticker.FixedFormatter([str(value) for value in tempo_ticks]))
        ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        ax.set_xlim(start, end)
        ax.set_ylabel("Local tempo (BPM)" if column == 0 else "")
        ax.grid(which="both", axis="y")
        if column == 0:
            ax.legend(
                frameon=True,
                facecolor="white",
                edgecolor="black",
                framealpha=1.0,
                fancybox=False,
                loc="upper left",
                ncol=2,
                fontsize=6.2,
            )

        ax = axes[2, column]
        local_margin = trace["confidence"][mask]
        local_time = candidate_times[mask]
        local_coefficient = coefficient(local_margin, frozen)
        ax.fill_between(local_time, local_margin, color=BLUE_LIGHT, alpha=0.65, step="mid")
        ax.plot(local_time, local_margin, color=BLUE, lw=0.8)
        ax.set_ylim(0, 0.6)
        ax.set_xlim(start, end)
        ax.set_ylabel("Margin $c_i$" if column == 0 else "")
        ax.set_xlabel("Time (s)")
        ax.set_yticks([0.0, 0.3, 0.6])
        ax.yaxis.set_minor_locator(mpl.ticker.FixedLocator([0.15, 0.45]))
        ax.grid(which="major", axis="y")
        ax.grid(which="minor", axis="y", color=LIGHT_GREY, linewidth=0.8)
        twin = ax.twinx()
        twin.plot(local_time, local_coefficient, color=ORANGE, lw=0.8, alpha=0.9)
        twin.set_ylim(0, 12)
        twin.set_ylabel("$w(c_i)$" if column == 1 else "", color=ORANGE)
        twin.tick_params(axis="y", colors=ORANGE)

        track_f1 = {
            method: float(record["track_metrics"][method]["beat_fmeasure"])
            for method in METHOD_ORDER
        }
        window_f1 = {
            method: float(window["method_f1"][method])
            for method in METHOD_ORDER
        }
        ax.text(
            0.01,
            0.96,
            "Window F1: " + format_f1(window_f1),
            transform=ax.transAxes,
            va="top",
            fontsize=5.7,
            color=CHARCOAL,
        )
        ax.text(
            0.01,
            0.82,
            (
                "CASM = Direct events exactly in this window"
                if role == "ambiguous"
                else "CASM beats Direct, DBN, and PLPDP in this window"
            ),
            transform=ax.transAxes,
            va="top",
            fontsize=5.7,
            color=CHARCOAL,
        )
        summary["columns"][role] = {
            "piece": record["piece"],
            "window": [start, end],
            "track_f1": track_f1,
            "window_f1": window_f1,
            "window_margin_mean": float(window["margin_mean"]),
            "window_margin_median": float(window["margin_median"]),
            "window_margin_max": float(window["margin_max"]),
            "casm_direct_exact": bool(window["casm_direct_exact"]),
            "manually_curated_window": override is not None,
        }

    handles = [
        Line2D([], [], color=CHARCOAL, marker="o", linestyle="None", markersize=5),
        Line2D([], [], color=BLUE, marker="|", linestyle="None", markersize=9, markeredgewidth=1.3),
        Line2D([], [], color=ORANGE, marker="x", linestyle="None", markersize=6, markeredgewidth=1.3),
        Line2D([], [], color=GREY, marker="^", linestyle="None", markersize=5),
        Line2D([], [], color=HEAT_RED, marker="o", markerfacecolor="none", linestyle="None", markersize=5, markeredgewidth=1.3),
    ]
    labels = ["Reference", "Direct", "CASM", "DBN (30–300 BPM)", "PLPDP"]
    fig.legend(
        handles,
        labels,
        frameon=False,
        ncol=5,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.105),
        handlelength=1.0,
        columnspacing=1.2,
        fontsize=8.0,
    )
    fig.text(
        0.02,
        0.02,
        "Post-hoc mechanism candidates, not performance estimates. Window F1 is used only to audit visible events; "
        "all CASM events remain on retained activation maxima.",
        fontsize=6.1,
        color=GREY,
    )
    stem = f"fig02b_candidate_{pair['id']}"
    save_all(fig, figure_dir, stem)
    summary["figure_stem"] = stem
    return summary


def main() -> None:
    args = parse_args()
    setup_style()
    search_dir = args.search_dir.resolve()
    manifest = json.loads((search_dir / "manifest.json").read_text())
    pairs = json.loads(args.pairs.read_text())
    frozen = manifest["frozen_parameters"]
    summaries: list[dict[str, object]] = []
    for pair in pairs:
        panel = str(pair["panel"])
        clear = find_record(manifest["records"], panel, "clear", str(pair["clear_piece"]))
        ambiguous = find_record(
            manifest["records"], panel, "ambiguous", str(pair["ambiguous_piece"])
        )
        summaries.append(
            render_pair(search_dir, args.figure_dir, pair, clear, ambiguous, frozen)
        )
    (search_dir / "gallery_summary.json").write_text(
        json.dumps(summaries, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"status": "COMPLETE", "figures": len(summaries)}, indent=2))


if __name__ == "__main__":
    main()
