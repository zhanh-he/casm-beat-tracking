"""Build/check the curated figure archive's exact-file provenance manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "MANIFEST.json"
GROUPS = (
    "01-used/figures",
    "01-used/source",
    "02-unused/historical",
    "02-unused/legacy-paper-preview",
    "02-unused/source",
    "02-unused/rejected-evaluation",
)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT.parent, text=True
    ).strip()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def archived_files() -> list[Path]:
    return sorted(
        file
        for group in GROUPS
        for file in (ROOT / group).rglob("*")
        if file.is_file()
        and file.relative_to(ROOT).as_posix()
        != "02-unused/rejected-evaluation/README.md"
    )


def source_for(relative: str, old: str, rejected: str, current: str) -> tuple[str, str]:
    if relative.startswith("01-used/figures/"):
        return current, "experiments/figures/" + relative.split("/", 2)[2]
    if relative == "01-used/source/run_dbn_calibration_scale.py":
        return current, "experiments/dbn/run_dbn_calibration_scale.py"
    previews = {
        "p0-main.png": "Paper/main/figures/p0.jpg",
        "p0-v5.png": "Paper/v5-intro-1st/figures/p0.jpg",
        "p1.png": "Paper/main/figures/p1.jpg",
        "p2.png": "Paper/main/figures/p2.jpg",
    }
    if relative.startswith("02-unused/legacy-paper-preview/"):
        return old, previews[relative.rsplit("/", 1)[1]]
    for prefix in ("01-used/source/", "02-unused/historical/", "02-unused/source/"):
        if relative.startswith(prefix):
            return old, relative.removeprefix(prefix)
    if relative.startswith("02-unused/rejected-evaluation/"):
        return rejected, relative.removeprefix("02-unused/rejected-evaluation/")
    raise ValueError(f"unmapped archived file: {relative}")


def refresh() -> None:
    old = git("rev-parse", "fe0b148^")
    rejected = git("rev-parse", "fe0b148")
    current = git("rev-parse", "d1c3341")
    entries = []
    for path in archived_files():
        relative = path.relative_to(ROOT).as_posix()
        source_commit, source_path = source_for(relative, old, rejected, current)
        source_blob = git("rev-parse", f"{source_commit}:{source_path}")
        local_blob = git("hash-object", str(path))
        if local_blob != source_blob:
            raise SystemExit(f"archive differs from source Git object: {relative}")
        entries.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest(path),
            "source_commit": source_commit,
            "source_path": source_path,
            "source_git_blob": source_blob,
        })
    payload = {
        "schema_version": 1,
        "scope": "curated CASM figure outputs and plotting sources; not benchmark validation",
        "files": entries,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Archived {len(entries)} exact-source files ({sum(x['bytes'] for x in entries)} bytes)")


def check() -> None:
    payload = json.loads(MANIFEST.read_text())
    entries = payload["files"]
    listed = {row["path"] for row in entries}
    present = {path.relative_to(ROOT).as_posix() for path in archived_files()}
    if listed != present:
        raise SystemExit(f"manifest mismatch: missing={sorted(listed-present)}, extra={sorted(present-listed)}")
    for row in entries:
        path = ROOT / row["path"]
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise SystemExit(f"archive checksum mismatch: {row['path']}")
    for archived in (ROOT / "01-used/figures").iterdir():
        canonical = ROOT.parent / "experiments/figures" / archived.name
        if not canonical.is_file() or digest(archived) != digest(canonical):
            raise SystemExit(f"selected figure differs from canonical output: {archived.name}")
    print(f"Archive verified: {len(entries)} files, {sum(x['bytes'] for x in entries)} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="regenerate only after verifying Git origins")
    arguments = parser.parse_args()
    refresh() if arguments.refresh else check()
