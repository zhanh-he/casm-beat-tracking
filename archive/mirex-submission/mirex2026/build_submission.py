#!/usr/bin/env python3
"""Build a self-contained, hashed MIREX multi-backbone source bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beat-this-root", type=Path, required=True)
    parser.add_argument("--casm-root", type=Path, required=True)
    parser.add_argument(
        "--beatthis-checkpoint",
        "--checkpoint",
        dest="beatthis_checkpoint",
        type=Path,
        required=True,
    )
    parser.add_argument("--mscnn-checkpoint", type=Path)
    parser.add_argument("--tcn-checkpoint", type=Path)
    parser.add_argument("--beatfm-checkpoint", type=Path)
    parser.add_argument("--beatfm-source-dir", type=Path,
                        help="Audited private BeatFM source; required with its checkpoint")
    parser.add_argument("--beatfm-mert-dir", type=Path,
                        help="Pinned MERT-v1-95M snapshot; required with BeatFM")
    parser.add_argument(
        "--casm-config", type=Path, default=ROOT / "config" / "casm-no-smc.json"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--checkpoint-role", required=True)
    parser.add_argument("--checkpoint-epoch", type=int, required=True)
    parser.add_argument("--training-run", required=True)
    parser.add_argument("--expected-checkpoint-sha256")
    parser.add_argument("--expected-mscnn-checkpoint-sha256")
    parser.add_argument("--expected-tcn-checkpoint-sha256")
    parser.add_argument("--expected-beatfm-checkpoint-sha256")
    parser.add_argument("--expected-casm-config-sha256")
    parser.add_argument("--mscnn-checkpoint-epoch", type=int)
    parser.add_argument("--tcn-checkpoint-epoch", type=int)
    parser.add_argument(
        "--mirex-task", choices=("beat", "downbeat", "both"), default="both",
        help="limit the packaged README to one task's organizer commands",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_python_package(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", ".idea", "__pycache__", "*.pyc", ".DS_Store"),
    )


def require_hash(path: Path, expected: str | None) -> str:
    actual = sha256_file(path)
    if expected is not None and actual != expected:
        raise RuntimeError(
            f"SHA256 mismatch for {path}: expected {expected}, got {actual}"
        )
    return actual


def main() -> None:
    args = parse_args()
    if bool(args.beatfm_checkpoint) != bool(args.beatfm_source_dir) or bool(args.beatfm_checkpoint) != bool(args.beatfm_mert_dir):
        raise ValueError("BeatFM checkpoint, source, and MERT snapshot must be bundled together")
    if args.tcn_checkpoint and args.beatfm_checkpoint:
        raise ValueError("three-backbone matrix excludes BeatFM assets")
    output = args.output_dir.resolve()
    if output.exists():
        raise RuntimeError(f"Refusing to replace existing output: {output}")
    checkpoint = args.beatthis_checkpoint.resolve()
    config = args.casm_config.resolve()
    casm_package = args.casm_root.resolve() / "src" / "casm_beat_tracking"
    for required in ("__init__.py", "config.py", "decoder.py"):
        if not (casm_package / required).is_file():
            raise FileNotFoundError(
                f"CASM source is incomplete; expected {casm_package / required}"
            )
    checkpoint_sha256 = require_hash(
        checkpoint, args.expected_checkpoint_sha256
    )
    config_sha256 = require_hash(config, args.expected_casm_config_sha256)

    output.mkdir(parents=True)
    for name in (
        ".dockerignore",
        "Dockerfile",
        "run.sh",
        "install.sh",
        "run_pipeline.py",
        "run_casm_beatthis.py",
        "requirements.txt",
        "requirements-dbn.txt",
        "requirements-plpdp.txt",
        "requirements-beatfm.txt",
        "SYSTEM_DESCRIPTION.md",
        "THIRD_PARTY.md",
    ):
        shutil.copy2(ROOT / name, output / name)
    if args.tcn_checkpoint:
        shutil.copy2(ROOT / "SYSTEM_DESCRIPTION_MATRIX.md", output / "SYSTEM_DESCRIPTION.md")
        shutil.copy2(ROOT / "THIRD_PARTY_MATRIX.md", output / "THIRD_PARTY.md")
    if args.tcn_checkpoint and not args.mscnn_checkpoint:
        raise ValueError("three-backbone matrix requires an MSCNN checkpoint")
    if args.tcn_checkpoint and args.mirex_task == "both":
        raise ValueError("three-backbone MIREX entries must be packaged separately by task")
    if args.mirex_task == "both":
        shutil.copy2(ROOT / "SUBMISSION_README.md", output / "README.md")
    else:
        substitutions = {
            "@TASK_TITLE@": (
                "Audio Beat Tracking" if args.mirex_task == "beat"
                else "Audio Downbeat Estimation"
            ),
            "@TASK@": args.mirex_task,
            "@EVENT@": "beat" if args.mirex_task == "beat" else "downbeat",
        }
        template = (
            "SUBMISSION_TASK_MATRIX_README.md" if args.tcn_checkpoint
            else "SUBMISSION_TASK_README.md"
        )
        readme = (ROOT / template).read_text()
        for token, value in substitutions.items():
            readme = readme.replace(token, value)
        (output / "README.md").write_text(readme)
    copy_python_package(ROOT / "mirex_pipeline", output / "mirex_pipeline")
    if args.tcn_checkpoint:
        copy_python_package(
            ROOT / "third_party" / "plpdp4beat",
            output / "third_party" / "plpdp4beat",
        )
    (output / "weights").mkdir()
    shutil.copy2(checkpoint, output / "weights" / "beatthis_mirex.ckpt")
    (output / "config").mkdir()
    shutil.copy2(config, output / "config" / "casm-no-smc.json")
    registry = json.loads((ROOT / "config" / "backbones.json").read_text())
    registry["backbones"]["beatthis"]["status"] = "ready-in-bundle"
    registry["backbones"]["mscnn"]["status"] = (
        "ready-in-bundle" if args.mscnn_checkpoint else "checkpoint-not-in-bundle"
    )
    registry["backbones"]["tcn"]["status"] = (
        "ready-in-bundle" if args.tcn_checkpoint else "checkpoint-not-in-bundle"
    )
    if args.tcn_checkpoint:
        registry["backbones"]["beatthis"]["description"] = (
            "No-SMC BeatThis train-split weight; seed 2, zero-based epoch 119 "
            "selected using allowed validation."
        )
        registry["backbones"].pop("beatfm")
    else:
        registry["backbones"]["beatfm"]["status"] = (
            "ready-in-bundle-private-assets" if args.beatfm_checkpoint else "checkpoint-not-in-bundle"
        )
    (output / "config" / "backbones.json").write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n"
    )

    backbone_records = {
        "beatthis": {
            "checkpoint": "weights/beatthis_mirex.ckpt",
            "role": args.checkpoint_role,
            "epoch": args.checkpoint_epoch,
            "training_run": args.training_run,
            "sha256": checkpoint_sha256,
        }
    }
    optional_checkpoints = (
        (
            "mscnn",
            args.mscnn_checkpoint,
            args.expected_mscnn_checkpoint_sha256,
        ),
        (
            "beatfm",
            args.beatfm_checkpoint,
            args.expected_beatfm_checkpoint_sha256,
        ),
        (
            "tcn",
            args.tcn_checkpoint,
            args.expected_tcn_checkpoint_sha256,
        ),
    )
    for name, source, expected in optional_checkpoints:
        if source is None:
            continue
        source = source.resolve()
        digest = require_hash(source, expected)
        relative = (
            f"weights/{name}_mirex.ckpt" if name in {"mscnn", "tcn"}
            else f"weights/{name}.ckpt"
        )
        shutil.copy2(source, output / relative)
        backbone_records[name] = {
            "checkpoint": relative,
            "sha256": digest,
            "epoch": (
                args.tcn_checkpoint_epoch if name == "tcn"
                else args.mscnn_checkpoint_epoch if name == "mscnn"
                else None
            ),
            "status": (
                "checkpoint-copied; adapter status is authoritative in "
                "config/backbones.json"
            ),
        }

    if args.beatfm_checkpoint:
        source_dir = args.beatfm_source_dir.resolve()
        mert_dir = args.beatfm_mert_dir.resolve()
        for required in ("MultilevelSemanticAggregation.py", "model.py"):
            if not (source_dir / required).is_file():
                raise FileNotFoundError(source_dir / required)
        for required in ("pytorch_model.bin", "config.json", "preprocessor_config.json", "modeling_MERT.py", "configuration_MERT.py"):
            if not (mert_dir / required).is_file():
                raise FileNotFoundError(mert_dir / required)
        copy_python_package(source_dir, output / "third_party" / "beatfm_source")
        shutil.copytree(
            mert_dir,
            output / "third_party" / "mert_v1_95m",
            ignore=shutil.ignore_patterns(".cache", "__pycache__", "*.pyc", ".DS_Store"),
        )
        (output / "backbone-retrain").mkdir()
        shutil.copy2(ROOT / "backbone-retrain" / "train_beatfm.py",
                     output / "backbone-retrain" / "train_beatfm.py")

    copy_python_package(
        args.beat_this_root.resolve() / "beat_this",
        output / "third_party" / "beat_this" / "beat_this",
    )
    beat_this_license = args.beat_this_root.resolve() / "LICENSE"
    if beat_this_license.is_file():
        (output / "third_party" / "beat_this").mkdir(
            parents=True, exist_ok=True
        )
        shutil.copy2(
            beat_this_license,
            output / "third_party" / "beat_this" / "LICENSE",
        )

    copy_python_package(
        casm_package,
        output / "vendor" / "casm" / "src" / "casm_beat_tracking",
    )
    casm_license = args.casm_root.resolve().parent / "LICENSE"
    if casm_license.is_file():
        (output / "vendor" / "casm").mkdir(parents=True, exist_ok=True)
        shutil.copy2(casm_license, output / "vendor" / "casm" / "LICENSE")

    files = {}
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        files[str(path.relative_to(output))] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    task_commands = {
        "beat": "./run.sh --task beat --backbone beatthis --decoder casm %input %output",
        "downbeat": "./run.sh --task downbeat --backbone beatthis --decoder casm %input %output",
    }
    organizer_commands = {}
    if args.tcn_checkpoint:
        for task in ("beat", "downbeat"):
            organizer_commands[task] = [
                f"./run.sh --task {task} --backbone {backbone} --decoder {decoder} %input %output"
                for backbone in ("beatthis", "mscnn", "tcn")
                for decoder in ("casm", "dbn55_215", "dbn30_300", "plpdp")
            ]
    if args.mirex_task != "both":
        task_commands = {args.mirex_task: task_commands[args.mirex_task]}
    manifest = {
        "schema_version": 1,
        "system": "CASM MIREX 2026 multi-backbone inference matrix",
        "mirex_task": args.mirex_task,
        "default_mirex_command": task_commands[
            args.mirex_task if args.mirex_task != "both" else "beat"
        ],
        "mirex_commands": task_commands,
        "organizer_commands": organizer_commands,
        "backbones": backbone_records,
        "casm_config_sha256": config_sha256,
        "files": files,
    }
    with (output / "MANIFEST.json").open("x") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")

    archive = shutil.make_archive(str(output), "gztar", output.parent, output.name)
    archive_path = Path(archive)
    print(
        json.dumps(
            {
                "output_dir": str(output),
                "archive": str(archive_path),
                "archive_sha256": sha256_file(archive_path),
                "beatthis_checkpoint_sha256": checkpoint_sha256,
                "casm_config_sha256": config_sha256,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
