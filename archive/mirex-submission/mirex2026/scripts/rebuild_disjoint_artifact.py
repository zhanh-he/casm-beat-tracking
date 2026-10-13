#!/usr/bin/env python3
"""Rebuild a target comparison using only eligibility-approved cached logits.

This migration does not infer logits again. It copies only permitted cache
panels, reruns every decoder, verifies old and new permitted aggregate values,
and leaves the source untouched until the corrected artifact is reviewed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from evaluation_policy import DATASET_PIECES, eligible_datasets, load_models


METHODS = {
    "direct": ("minimal", {}),
    "casm_no_smc": ("asm", None),
    "dbn_default": ("dbn", {}),
    "dbn_30_300": ("dbn", {"min_bpm": 30.0, "max_bpm": 300.0}),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evaluator", type=Path, required=True)
    parser.add_argument("--report-script", type=Path, required=True)
    parser.add_argument("--policy-script", type=Path, required=True)
    parser.add_argument("--casm-config", type=Path, required=True)
    parser.add_argument("--eval-project", type=Path, required=True)
    parser.add_argument("--train-project", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output or output.exists():
        raise SystemExit("output must be a new directory distinct from source")
    if not (source / "COMPLETE").is_file():
        raise SystemExit("source artifact is not complete")
    models_path = source / "manifest" / "models.tsv"
    models = load_models(models_path)
    old_rows = read_rows(source / "final" / "target_comparison.csv")
    old_lookup = {
        (row["model_id"], row["method"], row["dataset"]): row
        for row in old_rows
    }

    output.mkdir(parents=True)
    (output / "manifest").mkdir()
    shutil.copy2(models_path, output / "manifest" / "models.tsv")
    shutil.copy2(models_path, output / "manifest" / "models.frozen.tsv")
    (output / "raw").mkdir()
    (output / "cache").mkdir()
    (output / "logs").mkdir()
    (output / "final").mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        filter(
            None,
            [str(args.eval_project), str(args.train_project), env.get("PYTHONPATH", "")],
        )
    )
    env.update(
        PYTHONDONTWRITEBYTECODE="1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
    )
    casm_parameters = json.loads(args.casm_config.read_text())["decoder_parameters"]
    for model in models:
        name = model["model_id"]
        datasets = eligible_datasets(model)
        cache_paths: list[Path] = []
        for dataset in datasets:
            origin = source / "cache" / name / dataset
            destination = output / "cache" / name / dataset
            shutil.copytree(origin, destination)
            count = len(list(destination.glob("*.npz")))
            if count != DATASET_PIECES[dataset]:
                raise SystemExit(
                    f"cache panel mismatch model={name} dataset={dataset}: {count}"
                )
            cache_paths.append(destination)
        (output / "raw" / name).mkdir()
        for method, (decoder, parameters) in METHODS.items():
            if parameters is None:
                parameters = casm_parameters
            command = [
                sys.executable,
                str(args.evaluator),
            ]
            for cache_path in cache_paths:
                command += ["--cache-dir", str(cache_path)]
            command += [
                "--decoder", decoder,
                "--decoder-params", json.dumps(parameters, separators=(",", ":")),
                "--workers", "8",
                "--output-prefix", str(output / "raw" / name / method),
            ]
            log = output / "logs" / f"{name}.{method}.log"
            with log.open("w") as handle:
                subprocess.run(command, env=env, stdout=handle, stderr=subprocess.STDOUT, check=True)

    subprocess.run(
        [
            sys.executable,
            str(args.report_script),
            "--evaluation-root", str(output),
            "--models", str(output / "manifest" / "models.tsv"),
            "--casm-config", str(args.casm_config),
        ],
        env=env,
        check=True,
    )
    new_rows = read_rows(output / "final" / "target_comparison.csv")
    expected_keys = {
        (model["model_id"], method, dataset)
        for model in models
        for method in METHODS
        for dataset in eligible_datasets(model)
    }
    actual_keys = {
        (row["model_id"], row["method"], row["dataset"])
        for row in new_rows
    }
    if actual_keys != expected_keys:
        raise SystemExit(f"corrected row keys differ: {actual_keys ^ expected_keys}")
    for row in new_rows:
        key = row["model_id"], row["method"], row["dataset"]
        old = old_lookup[key]
        for metric in ("beat_fmeasure", "beat_cmlt", "beat_amlt"):
            if abs(float(row[metric]) - float(old[metric])) > 1e-12:
                raise SystemExit(f"permitted result changed: {key} {metric}")

    provenance = {
        "source_artifact": str(source),
        "source_result_sha256": sha256(source / "final" / "target_comparison.csv"),
        "removed_model_dataset_pairs": [
            {"model_id": row["model_id"], "dataset": row["dataset"]}
            for row in old_rows
            if row["dataset"] not in eligible_datasets(next(
                model for model in models if model["model_id"] == row["model_id"]
            ))
        ],
        "policy_sha256": sha256(args.policy_script),
        "report_sha256": sha256(args.report_script),
        "rebuild_script_sha256": sha256(Path(__file__)),
    }
    (output / "manifest" / "correction.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    for area, pattern, manifest_name in (
        ("cache", "*.npz", "cache_sha256.txt"),
        ("raw", "*", "results_sha256.txt"),
    ):
        paths = sorted(path for path in (output / area).rglob(pattern) if path.is_file())
        (output / "manifest" / manifest_name).write_text(
            "".join(f"{sha256(path)}  {path.relative_to(output)}\n" for path in paths)
        )
    (output / "COMPLETE").write_text("disjoint-panel correction complete\n")
    print(f"corrected_artifact={output} rows={len(new_rows)}")


if __name__ == "__main__":
    main()
