#!/usr/bin/env python3
"""Render Figure 2b with the original content and only DBN corrected."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


CHARCOAL = "#252a30"
GREY = "#838b93"
LIGHT_GREY = "#dfe3e7"
BLUE = "#4173c8"
RED = "#cd5c5c"
OLIVE = "#758a39"

CASES = (
    ("smc_001_corrected.npz", "(a)  Clear periodicity: SMC_001", 15.5, 27.5),
    ("smc_032_corrected.npz", "(b)  Ambiguous periodicity: SMC_032", 7.25, 19.25),
)


def selected_trace(
    trace: dict[str, np.ndarray], events: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Recover the original Figure 2b CASM values at final CASM events."""
    candidate_times = np.asarray(trace["candidates"], dtype=float) / float(trace["fps"])
    if not len(candidate_times) or not len(events):
        empty = np.empty(0, dtype=float)
        return empty, empty, empty
    indices = np.asarray([np.argmin(np.abs(candidate_times - event)) for event in events])
    return (
        candidate_times[indices],
        np.asarray(trace["periods"], dtype=float)[indices],
        np.asarray(trace["confidence"], dtype=float)[indices],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def within(values: np.ndarray, start: float, end: float) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return values[(values >= start) & (values <= end)]


def scatter_events(ax, values, y, color, marker, start, end, *, hollow=False, size=27):
    values = within(values, start, end)
    kwargs = {"s": size, "marker": marker, "linewidths": 1.15, "zorder": 8}
    if hollow:
        kwargs.update(facecolors="white", edgecolors=color)
    else:
        kwargs.update(color=color)
    ax.scatter(values, np.full(len(values), y), **kwargs)


def coefficient(confidence: np.ndarray, frozen: dict[str, object]) -> np.ndarray:
    sigma0 = float(frozen["duration_sigma"])
    sigmau = float(frozen["uncertain_sigma"])
    lam = float(frozen["duration_weight"])
    return lam * confidence / (2.0 * (sigma0 + (1.0 - confidence) * sigmau) ** 2)


def main() -> None:
    args = parse_args()
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.4,
            "axes.titlesize": 10.0,
            "axes.labelsize": 8.8,
            "axes.linewidth": 0.75,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 7.3,
            "figure.dpi": 180,
            "savefig.dpi": 320,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    frozen = json.loads(args.manifest.read_text())["frozen_parameters"]
    fig, axes = plt.subplots(
        3,
        2,
        figsize=(7.15, 5.0),
        gridspec_kw={"height_ratios": [1.62, 0.98, 0.88]},
    )
    fig.subplots_adjust(left=0.095, right=0.92, top=0.92, bottom=0.20, wspace=0.25, hspace=0.23)

    for column, (filename, title, start, end) in enumerate(CASES):
        with np.load(args.data_dir / filename, allow_pickle=False) as archive:
            trace = {key: archive[key] for key in archive.files}
        fps = float(trace["fps"])
        frame_start = max(0, int(np.floor(start * fps)))
        frame_end = min(len(trace["beat_prob"]), int(np.ceil(end * fps)) + 1)
        times = np.arange(frame_start, frame_end) / fps

        ax = axes[0, column]
        activation = trace["beat_prob"][frame_start:frame_end]
        ax.fill_between(times, activation, color=LIGHT_GREY, alpha=0.42, lw=0)
        ax.plot(times, activation, color=GREY, lw=1.0)
        scatter_events(ax, trace["truth_beat"], -0.055, CHARCOAL, "o", start, end, size=22)
        scatter_events(ax, trace["direct_beat"], -0.165, GREY, "|", start, end, size=42)
        scatter_events(ax, trace["casm_beat"], -0.275, BLUE, "o", start, end, hollow=True, size=25)
        scatter_events(ax, trace["dbn_beat_corrected"], -0.385, RED, "^", start, end, hollow=True, size=27)
        scatter_events(ax, trace["plpdp_beat"], -0.495, OLIVE, "x", start, end, size=27)
        ax.set_xlim(start, end)
        ax.set_ylim(-0.54, 1.03)
        ax.set_yticks([0.0, 0.5, 1.0])
        ax.set_ylabel("Beat activation" if column == 0 else "")
        ax.set_title(title, fontweight="bold", pad=7)
        ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.6)
        ax.tick_params(axis="x", labelbottom=False)

        casm_events = within(trace["casm_beat"], start, end)
        target_times, target_periods, selected_confidence = selected_trace(trace, casm_events)
        mask = (target_times >= start) & (target_times <= end)
        target_times = target_times[mask]
        target_periods = target_periods[mask]
        selected_confidence = selected_confidence[mask]

        ax = axes[1, column]
        ax.scatter(
            target_times,
            60.0 * fps / target_periods,
            facecolors="white",
            edgecolors=BLUE,
            s=23,
            linewidths=1.1,
            label="CASM local target",
            zorder=6,
        )
        truth = np.asarray(trace["truth_beat"], dtype=float)
        truth_time = 0.5 * (truth[:-1] + truth[1:])
        truth_bpm = 60.0 / np.diff(truth)
        truth_mask = (truth_time >= start) & (truth_time <= end)
        ax.plot(
            truth_time[truth_mask],
            truth_bpm[truth_mask],
            color=CHARCOAL,
            marker="o",
            markersize=3.2,
            linewidth=1.15,
            label="Reference IBI",
        )
        ax.set_yscale("log")
        ax.set_ylim(28, 310)
        ax.set_xlim(start, end)
        ticks = [30, 60, 120, 300]
        ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ticks))
        ax.yaxis.set_major_formatter(mpl.ticker.FixedFormatter([str(tick) for tick in ticks]))
        ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        ax.set_ylabel("Local tempo (BPM)" if column == 0 else "")
        ax.tick_params(axis="x", labelbottom=False)
        ax.grid(which="both", axis="y", color=LIGHT_GREY, linewidth=0.6)
        if column == 0:
            ax.legend(loc="upper left", ncol=2, frameon=True, fancybox=False, edgecolor=CHARCOAL)

        ax = axes[2, column]
        weights = coefficient(selected_confidence, frozen)
        ax.plot(target_times, selected_confidence, color=BLUE, linewidth=1.25, label=r"CASM margin $c_i$")
        ax.set_ylim(0.0, 0.6)
        ax.set_yticks([0.0, 0.3, 0.6])
        ax.set_xlim(start, end)
        ax.set_ylabel(r"Margin $c_i$" if column == 0 else "")
        ax.set_xlabel("Time (s)")
        ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.6)
        twin = ax.twinx()
        twin.plot(target_times, weights, color=BLUE, linestyle="--", linewidth=1.1, label=r"Weight $w(c_i)$")
        twin.set_ylim(0.0, 11.0)
        twin.set_yticks([0, 10])
        twin.tick_params(axis="y", colors=BLUE)
        twin.set_ylabel(r"$w(c_i)$" if column == 1 else "", color=BLUE)
        if column == 1:
            handles = [
                Line2D([], [], color=BLUE, lw=1.25, label=r"CASM margin $c_i$"),
                Line2D([], [], color=BLUE, lw=1.1, ls="--", label=r"Weight $w(c_i)$"),
            ]
            ax.legend(handles=handles, loc="upper right", ncol=2, frameon=True, fancybox=False, edgecolor=CHARCOAL)

    handles = [
        Line2D([], [], color=CHARCOAL, marker="o", linestyle="None", markersize=5),
        Line2D([], [], color=GREY, marker="|", linestyle="None", markersize=9, markeredgewidth=1.3),
        Line2D([], [], color=BLUE, marker="o", markerfacecolor="white", linestyle="None", markersize=5, markeredgewidth=1.3),
        Line2D([], [], color=RED, marker="^", markerfacecolor="white", linestyle="None", markersize=5, markeredgewidth=1.2),
        Line2D([], [], color=OLIVE, marker="x", linestyle="None", markersize=6, markeredgewidth=1.3),
    ]
    labels = ["Reference", "Direct", "CASM", "DBN (30–300 BPM)", "PLPDP"]
    fig.legend(
        handles,
        labels,
        frameon=False,
        ncol=5,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.095),
        handlelength=1.0,
        columnspacing=1.25,
    )
    fig.text(
        0.012,
        0.025,
        "Post-hoc mechanism candidates, not performance estimates. Window F1 is used only to audit visible events; "
        "all CASM events remain on retained activation maxima.",
        fontsize=6.4,
        color=GREY,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight", facecolor="white", dpi=320)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
