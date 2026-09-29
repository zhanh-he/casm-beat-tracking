#!/usr/bin/env python3
"""Assemble strict target-only Direct/CASM/DBN comparison tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean

from evaluation_policy import DATASET_PIECES, eligible_datasets, load_models


METHODS = ("direct", "casm_no_smc", "dbn_default", "dbn_30_300")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_mean(rows: list[dict[str, str]], key: str, context: str) -> float:
    if not rows:
        raise SystemExit(f"empty required group: {context}")
    values: list[float] = []
    for index, row in enumerate(rows):
        try:
            value = float(row[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(f"missing/non-numeric {context}.{key}[{index}]") from exc
        if not math.isfinite(value):
            raise SystemExit(f"non-finite {context}.{key}[{index}]={value!r}")
        values.append(value)
    return fmean(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--casm-config", type=Path, required=True)
    args = parser.parse_args()

    models = load_models(args.models)

    rows_out: list[dict[str, object]] = []
    provenance: list[dict[str, object]] = []
    reference_panels: dict[str, list[tuple[str, str]]] = {}
    for model in models:
        model_id = model["model_id"]
        checkpoint = Path(model["checkpoint"]).resolve()
        if not checkpoint.is_file():
            raise SystemExit(f"missing checkpoint: {checkpoint}")
        provenance.append(
            {
                **model,
                "checkpoint": str(checkpoint),
                "checkpoint_sha256": sha256(checkpoint),
            }
        )
        permitted = eligible_datasets(model)
        for method in METHODS:
            path = args.evaluation_root / "raw" / model_id / f"{method}.pieces.csv"
            if not path.is_file():
                raise SystemExit(f"missing result: {path}")
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            unexpected = {row["dataset"] for row in rows} - set(permitted)
            if unexpected:
                raise SystemExit(
                    f"training/evaluation overlap or unapproved panel: "
                    f"model={model_id} method={method} datasets={sorted(unexpected)}"
                )
            panel = sorted((row["piece"], row["dataset"]) for row in rows)
            if len(panel) != len(set(panel)):
                raise SystemExit(f"duplicate piece rows: {path}")
            if method == "direct":
                reference_panels[model_id] = panel
            elif panel != reference_panels[model_id]:
                raise SystemExit(f"piece panel mismatch: model={model_id} method={method}")
            for dataset in permitted:
                subset = [row for row in rows if row["dataset"] == dataset]
                expected = DATASET_PIECES[dataset]
                if len(subset) != expected:
                    raise SystemExit(
                        f"piece count mismatch model={model_id} method={method} "
                        f"dataset={dataset}: {len(subset)} != {expected}"
                    )
                result: dict[str, object] = {
                    "model_id": model_id,
                    "smc_training_status": model["smc_training_status"],
                    "method": method,
                    "dataset": dataset,
                    "pieces": len(subset),
                }
                for target in ("beat", "downbeat"):
                    for name in ("fmeasure", "cmlt", "amlt"):
                        key = f"{target}_{name}"
                        if dataset == "smc" and target == "downbeat":
                            result[key] = None
                        else:
                            result[key] = required_mean(
                                subset, key, f"{model_id}.{method}.{dataset}"
                            )
                rows_out.append(result)

    output_dir = args.evaluation_root / "final"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "target_comparison.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_out[0]))
        writer.writeheader()
        writer.writerows(rows_out)
    payload = {
        "scope": "target diagnostics only; never checkpoint selection",
        "methods": list(METHODS),
        "datasets": sorted({row["dataset"] for row in rows_out}),
        "eligibility_rule": (
            "Each model is scored only on datasets absent from its training pool; "
            "unknown provenance and overlapping rows fail closed."
        ),
        "model_provenance": provenance,
        "casm_no_smc": {
            "config": str(args.casm_config.resolve()),
            "config_sha256": sha256(args.casm_config),
            "payload": json.loads(args.casm_config.read_text()),
        },
        "rows": rows_out,
    }
    (output_dir / "target_comparison.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(f"report_complete rows={len(rows_out)} output={csv_path}")


if __name__ == "__main__":
    main()
