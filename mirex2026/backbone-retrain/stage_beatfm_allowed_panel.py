"""Stage only the audited 137-song BeatFM validation panel for inference.

The exact 911-row source manifest is preserved byte-for-byte so a relocated
inference host can verify the checkpoint training split by its SHA-256. Audio
and annotations are copied privately; do not publish the resulting archive.
"""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import shutil

from train_beatfm import read_manifest


FIELDS = ("dataset", "stem", "split", "audio_path", "annotation_path",
          "annotation_time_shift_seconds", "beat_count", "downbeat_count")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error(f"refusing to overwrite: {args.output_dir}")
    records, digest = read_manifest(args.manifest, verified_subset=True)
    validation = [record for record in records if record.split == "val"]
    if len(validation) != 137 or sum(r.dataset == "ballroom" for r in validation) != 103:
        raise ValueError("unexpected Ballroom/RWC validation inventory")
    output = args.output_dir
    output.mkdir(parents=True)
    shutil.copy2(args.manifest, output / "source_manifest.tsv")
    relocated = []
    for record in validation:
        if Path(record.stem).name != record.stem:
            raise ValueError(f"unsafe stem: {record.stem}")
        audio_rel = Path("audio") / record.dataset / f"{record.stem}{record.audio_path.suffix.lower()}"
        annotation_rel = Path("annotation") / record.dataset / f"{record.stem}{record.annotation_path.suffix.lower()}"
        audio_dst = output / audio_rel
        annotation_dst = output / annotation_rel
        audio_dst.parent.mkdir(parents=True, exist_ok=True)
        annotation_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(record.audio_path, audio_dst)
        shutil.copy2(record.annotation_path, annotation_dst)
        relocated.append({
            "dataset": record.dataset, "stem": record.stem, "split": record.split,
            "audio_path": str(audio_rel), "annotation_path": str(annotation_rel),
            "annotation_time_shift_seconds": f"{record.annotation_time_shift_seconds:.3f}",
            "beat_count": record.beat_count, "downbeat_count": record.downbeat_count,
        })
    with (output / "validation_relocated.tsv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(relocated)
    (output / "provenance.json").write_text(json.dumps({
        "role": "private transfer of allowed Ballroom/RWC validation only",
        "source_manifest_sha256": digest,
        "validation_pieces": len(relocated),
        "ballroom_pieces": 103,
        "rwc_pieces": 34,
        "target_datasets_used": [],
    }, indent=2) + "\n")
    (output / "COMPLETE").write_text("staged allowed validation panel\n")
    print(json.dumps({"output_dir": str(output), "source_manifest_sha256": digest,
                      "validation_pieces": len(relocated)}), flush=True)


if __name__ == "__main__":
    main()
