#!/usr/bin/env python3
"""Replace only the DBN marker row in the original Figure 2b PNG.

The original panel is the rendering authority for every non-DBN pixel.  The
script detects its two red DBN rows, estimates each time-to-pixel transform
from the original DBN events, clears only those narrow rows, and draws the
corrected beat-only DBN events.  It then verifies that no pixel outside the
two DBN strips changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


CASES = (
    ("001", 15.5, 27.5),
    ("032", 7.25, 19.25),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-figure", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--corrected-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contiguous_groups(values: np.ndarray, max_gap: int = 2) -> list[np.ndarray]:
    if not len(values):
        return []
    split = np.flatnonzero(np.diff(values) > max_gap) + 1
    return [group for group in np.split(values, split) if len(group)]


def draw_antialiased_triangle(
    image: Image.Image,
    center_x: float,
    center_y: float,
    color: tuple[int, int, int],
) -> None:
    scale = 4
    half_width = 10.5
    half_height = 10.5
    pad = 4
    size = int(2 * (max(half_width, half_height) + pad))
    overlay = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = size * scale / 2
    cy = size * scale / 2
    points = [
        (cx, cy - half_height * scale),
        (cx - half_width * scale, cy + half_height * scale),
        (cx + half_width * scale, cy + half_height * scale),
        (cx, cy - half_height * scale),
    ]
    draw.line(points, fill=(*color, 255), width=3 * scale, joint="curve")
    overlay = overlay.resize((size, size), Image.Resampling.LANCZOS)
    left = int(round(center_x - size / 2))
    top = int(round(center_y - size / 2))
    image.paste(overlay, (left, top), overlay)


def main() -> None:
    args = parse_args()
    original = Image.open(args.source_figure).convert("RGB")
    original_pixels = np.asarray(original)
    red = original_pixels[:, :, 0]
    green = original_pixels[:, :, 1]
    blue = original_pixels[:, :, 2]
    y_grid = np.indices(red.shape)[0]
    red_mask = (
        (y_grid < int(original.height * 0.45))
        & (red > 150)
        & (red.astype(int) - green.astype(int) > 45)
        & (red.astype(int) - blue.astype(int) > 35)
        & (green < 170)
    )
    marker_y, marker_x = np.where(red_mask)
    if not len(marker_x):
        raise RuntimeError("could not detect the original red DBN markers")
    red_color = tuple(int(value) for value in np.median(original_pixels[red_mask], axis=0))
    x_components = contiguous_groups(np.unique(marker_x))
    centers = np.asarray([(group[0] + group[-1]) / 2 for group in x_components])
    center_split = int(np.argmax(np.diff(centers))) + 1
    center_groups = (centers[:center_split], centers[center_split:])

    result = original.copy()
    receipt: dict[str, object] = {
        "status": "COMPLETE",
        "policy": "Only pixels inside the two detected DBN marker strips may change.",
        "source_figure": args.source_figure.name,
        "source_figure_sha256": sha256(args.source_figure),
        "dbn_color_rgb": list(red_color),
        "cases": {},
    }
    permitted = np.zeros((original.height, original.width), dtype=bool)
    marker_top = int(marker_y.min()) - 4
    marker_bottom = int(marker_y.max()) + 5

    for (case, start, end), old_centers in zip(CASES, center_groups, strict=True):
        trace_path = args.trace_dir / f"bt_smc_oof__smc__smc_{case}.npz"
        corrected_path = args.corrected_dir / f"smc_{case}_corrected.npz"
        with np.load(trace_path, allow_pickle=False) as trace:
            old_events = np.asarray(trace["dbn_matched_beat"], dtype=float)
        with np.load(corrected_path, allow_pickle=False) as corrected:
            new_events = np.asarray(corrected["dbn_beat_corrected"], dtype=float)
        old_events = old_events[(old_events >= start) & (old_events <= end)]
        new_events = new_events[(new_events >= start) & (new_events <= end)]
        if len(old_events) != len(old_centers):
            raise RuntimeError(
                f"SMC {case}: detected {len(old_centers)} markers but expected {len(old_events)}"
            )

        slope, intercept = np.polyfit(old_events, old_centers, 1)
        residual = old_centers - (slope * old_events + intercept)
        rmse = float(np.sqrt(np.mean(residual**2)))
        if rmse > 1.0:
            raise RuntimeError(f"SMC {case}: time-to-pixel fit RMSE is {rmse:.3f} px")
        # Stay one pixel inside the fitted axes so the original spines remain
        # byte-for-byte untouched. Marker antialiasing may extend over a spine,
        # exactly as a normal scatter marker would, but the clearing pass may not.
        axis_left = max(0, int(math.floor(slope * start + intercept)) + 1)
        axis_right = min(original.width, int(math.ceil(slope * end + intercept)) - 1)
        ImageDraw.Draw(result).rectangle(
            (axis_left, marker_top, axis_right - 1, marker_bottom - 1),
            fill=(255, 255, 255),
        )
        center_y = (marker_y.min() + marker_y.max()) / 2
        new_centers = slope * new_events + intercept
        permitted_left = max(0, min(axis_left, int(math.floor(new_centers.min())) - 15))
        permitted_right = min(
            original.width, max(axis_right, int(math.ceil(new_centers.max())) + 16)
        )
        permitted[marker_top:marker_bottom, permitted_left:permitted_right] = True
        for event in new_events:
            draw_antialiased_triangle(result, slope * event + intercept, center_y, red_color)

        receipt["cases"][f"SMC_{case}"] = {
            "window_seconds": [start, end],
            "old_dbn_event_count": int(len(old_events)),
            "corrected_dbn_event_count": int(len(new_events)),
            "time_to_pixel_slope": float(slope),
            "time_to_pixel_intercept": float(intercept),
            "fit_rmse_pixels": rmse,
            "cleared_pixel_strip": [axis_left, marker_top, axis_right, marker_bottom],
            "permitted_pixel_strip": [
                permitted_left,
                marker_top,
                permitted_right,
                marker_bottom,
            ],
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, dpi=original.info.get("dpi", (320, 320)))
    output_pixels = np.asarray(Image.open(args.output).convert("RGB"))
    difference = np.any(original_pixels != output_pixels, axis=2)
    outside = difference & ~permitted
    if np.any(outside):
        raise RuntimeError(f"{int(outside.sum())} pixels changed outside DBN strips")
    receipt["output_figure"] = args.output.name
    receipt["output_figure_sha256"] = sha256(args.output)
    receipt["changed_pixel_count"] = int(difference.sum())
    receipt["changed_pixels_outside_dbn_strips"] = int(outside.sum())
    receipt["unchanged_pixel_count"] = int((~difference).sum())
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
