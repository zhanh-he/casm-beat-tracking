from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "backbone-retrain" / "train_beatfm.py"
SPEC = importlib.util.spec_from_file_location("train_beatfm", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class BeatFMTrainPreflightTest(unittest.TestCase):
    def test_partial_manifest_requires_explicit_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "audio.wav"
            annotation = root / "beats.txt"
            audio.write_bytes(b"raw audio existence only")
            annotation.write_text("0.5 1\n")
            manifest = root / "pilot.tsv"
            with manifest.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=(
                    "dataset", "stem", "split", "audio_path", "annotation_path",
                    "beat_count", "downbeat_count",
                ), delimiter="\t")
                writer.writeheader()
                for index in range(100):
                    writer.writerow({
                        "dataset": "ballroom", "stem": f"song_{index}",
                        "split": "train" if index < 80 else "val",
                        "audio_path": audio, "annotation_path": annotation,
                        "beat_count": 1, "downbeat_count": 1,
                    })
            with self.assertRaisesRegex(ValueError, "3783-train/556-val"):
                module.read_manifest(manifest)
            rows, digest = module.read_manifest(manifest, pilot_partial_audio=True)
            self.assertEqual(len(rows), 100)
            self.assertEqual(len(digest), 64)

    def test_pilot_still_forbids_smc(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "audio.wav"
            annotation = root / "beats.txt"
            audio.write_bytes(b"wave")
            annotation.write_text("0.5 1\n")
            manifest = root / "bad.tsv"
            manifest.write_text(
                "dataset\tstem\tsplit\taudio_path\tannotation_path\tbeat_count\tdownbeat_count\n"
                f"smc\tsong\ttrain\t{audio}\t{annotation}\t1\t1\n"
            )
            with self.assertRaisesRegex(ValueError, "forbidden development piece"):
                module.read_manifest(manifest, pilot_partial_audio=True)

    def test_verified_subset_requires_exact_audited_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "audio.wav"
            annotation = root / "beats.txt"
            audio.touch()
            annotation.write_text("0.5 1\n")
            manifest = root / "subset.tsv"
            with manifest.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=(
                    "dataset", "stem", "split", "audio_path", "annotation_path",
                    "annotation_time_shift_seconds", "beat_count", "downbeat_count",
                ), delimiter="\t")
                writer.writeheader()
                for index in range(911):
                    dataset = "ballroom" if index < 685 else "rwc"
                    local_index = index if dataset == "ballroom" else index - 685
                    writer.writerow({
                        "dataset": dataset,
                        "stem": f"song_{index}",
                        "split": "train" if local_index < (582 if dataset == "ballroom" else 192) else "val",
                        "audio_path": audio, "annotation_path": annotation,
                        "annotation_time_shift_seconds": "-0.218" if index == 700 else "0",
                        "beat_count": 1, "downbeat_count": 1,
                    })
            with self.assertRaisesRegex(ValueError, "3783-train/556-val"):
                module.read_manifest(manifest)
            rows, digest = module.read_manifest(manifest, verified_subset=True)
            self.assertEqual(len(rows), 911)
            self.assertEqual(rows[700].annotation_time_shift_seconds, -0.218)
            self.assertEqual(len(digest), 64)

    def test_expanded_subset_is_count_and_dataset_gated(self) -> None:
        counts = {
            "ballroom": (582, 103), "rwc": (192, 34),
            "hainsworth": (189, 33), "candombe": (30, 5),
            "groove_midi": (285, 51), "guitarset": (153, 27),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "audio.wav"
            annotation = root / "beats.txt"
            audio.touch()
            annotation.write_text("0.5 1\n")
            manifest = root / "expanded.tsv"
            with manifest.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=(
                    "dataset", "stem", "split", "audio_path", "annotation_path",
                    "beat_count", "downbeat_count",
                ), delimiter="\t")
                writer.writeheader()
                for dataset, (train_count, val_count) in counts.items():
                    for index in range(train_count + val_count):
                        writer.writerow({
                            "dataset": dataset, "stem": f"{dataset}_{index}",
                            "split": "train" if index < train_count else "val",
                            "audio_path": audio, "annotation_path": annotation,
                            "beat_count": 1, "downbeat_count": 1,
                        })
            rows, digest = module.read_manifest(manifest, expanded_verified_subset=True)
            self.assertEqual(len(rows), 1684)
            self.assertEqual(len(digest), 64)
            with self.assertRaisesRegex(ValueError, "mutually exclusive"):
                module.read_manifest(manifest, verified_subset=True,
                                     expanded_verified_subset=True)


if __name__ == "__main__":
    unittest.main()
