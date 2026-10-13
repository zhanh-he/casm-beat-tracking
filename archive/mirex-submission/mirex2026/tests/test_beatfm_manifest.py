from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "backbone-retrain" / "beatfm_manifest.py"
SPEC = importlib.util.spec_from_file_location("beatfm_manifest", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class BeatFMManifestTest(unittest.TestCase):
    def test_no_smc_gtzan_and_audio_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for dataset, split in (("beatles", "train"), ("ballroom", "val"), ("smc", "train")):
                folder = root / "annotations" / dataset
                (folder / "annotations" / "beats").mkdir(parents=True)
                (folder / "single.split").write_text(f"{dataset}_song\t{split}\n")
                (folder / "annotations" / "beats" / f"{dataset}_song.beats").write_text("-0.02\t1\n1.0\t1\n2.0\t2\n")
            summary = module.build_manifest(root / "annotations")
            self.assertEqual(summary["allowed_train_pieces"], 1)
            self.assertEqual(summary["allowed_val_pieces"], 1)
            self.assertNotIn("smc", summary["per_dataset"])
            with self.assertRaisesRegex(ValueError, "original audio files missing"):
                module.build_manifest(root / "annotations", audio_root=root / "audio", output=root / "manifest.tsv")
            self.assertFalse((root / "manifest.tsv").exists())
            for dataset in ("beatles", "ballroom"):
                folder = root / "audio" / dataset
                folder.mkdir(parents=True)
                (folder / f"{dataset}_song.wav").write_bytes(b"not decoded by manifest preflight")
            summary = module.build_manifest(root / "annotations", audio_root=root / "audio", output=root / "manifest.tsv")
            self.assertEqual(summary["missing_audio_count"], 0)
            self.assertTrue((root / "manifest.tsv").exists())

    def test_partial_audio_is_explicitly_pilot_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for dataset, split in (("ballroom", "train"), ("rwc", "val"), ("beatles", "train")):
                folder = root / "annotations" / dataset
                (folder / "annotations" / "beats").mkdir(parents=True)
                (folder / "single.split").write_text(f"{dataset}_song\t{split}\n")
                (folder / "annotations" / "beats" / f"{dataset}_song.beats").write_text("0.5\t1\n")
            audio = root / "audio"
            for dataset in ("ballroom", "rwc"):
                (audio / dataset).mkdir(parents=True)
                (audio / dataset / f"{dataset}_song.wav").write_bytes(b"waveform gate checks only existence")
            output = root / "pilot.tsv"
            with self.assertRaisesRegex(ValueError, "original audio files missing"):
                module.build_manifest(root / "annotations", audio_root=audio, output=output)
            summary = module.build_manifest(
                root / "annotations", audio_root=audio, output=output,
                pilot_partial_audio=True,
            )
            self.assertEqual(summary["manifest_role"], "pilot_partial_audio_not_submission")
            self.assertEqual(summary["missing_audio_count"], 1)
            self.assertEqual(len(output.read_text().splitlines()), 3)

    def test_audio_release_offset_is_carried_into_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "annotations" / "rwc"
            (folder / "annotations" / "beats").mkdir(parents=True)
            (folder / "single.split").write_text("rwc_song\ttrain\nrwc_song2\tval\n")
            for stem in ("rwc_song", "rwc_song2"):
                (folder / "annotations" / "beats" / f"{stem}.beats").write_text("0.5 1\n")
            wav = root / "rwc.wav"
            wav.write_bytes(b"wave")
            audio_map = root / "map.tsv"
            audio_map.write_text(
                "dataset\tstem\taudio_path\tannotation_time_shift_seconds\n"
                f"rwc\trwc_song\t{wav}\t-0.218\n"
                f"rwc\trwc_song2\t{wav}\t0.000\n"
            )
            output = root / "manifest.tsv"
            summary = module.build_manifest(folder.parent, audio_map_path=audio_map, output=output)
            self.assertEqual(summary["mapped_shifted_annotation_pieces"], 1)
            self.assertIn("-0.218", output.read_text())

    def test_verified_subset_is_explicit_and_count_gated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for dataset, count_train, count_val in (("ballroom", 582, 103), ("rwc", 192, 34)):
                folder = root / "annotations" / dataset
                beats = folder / "annotations" / "beats"
                beats.mkdir(parents=True)
                lines = []
                for index in range(count_train + count_val):
                    stem = f"{dataset}_{index:04d}"
                    lines.append(f"{stem}\t{'train' if index < count_train else 'val'}\n")
                    (beats / f"{stem}.beats").write_text("0.5 1\n")
                    audio = root / "audio" / dataset
                    audio.mkdir(parents=True, exist_ok=True)
                    (audio / f"{stem}.wav").touch()
                (folder / "single.split").write_text("".join(lines))
            output = root / "subset.tsv"
            summary = module.build_manifest(
                root / "annotations", audio_root=root / "audio",
                verified_subset=True, output=output,
            )
            self.assertEqual(summary["manifest_role"], "verified_ballroom_rwc_subset_candidate")
            self.assertEqual(summary["mapped_train_pieces"], 774)
            self.assertEqual(summary["mapped_val_pieces"], 137)
            self.assertEqual(len(output.read_text().splitlines()), 912)


if __name__ == "__main__":
    unittest.main()
