"""Small artifact-structure tests; real checkpoints are smoke-tested separately."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BuildSubmissionTest(unittest.TestCase):
    def test_three_backbone_task_bundle_lists_exactly_nine_variants(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            beat_this = base / "beat_this_source"
            (beat_this / "beat_this").mkdir(parents=True)
            (beat_this / "beat_this" / "__init__.py").write_text("")
            casm = base / "casm"
            (casm / "src" / "casm_beat_tracking").mkdir(parents=True)
            (casm / "src" / "casm_beat_tracking" / "__init__.py").write_text("")
            weights = {}
            for name in ("beatthis", "mscnn", "tcn"):
                path = base / f"{name}.ckpt"
                path.write_bytes(name.encode())
                weights[name] = path
            output = base / "beat_bundle"
            command = [
                sys.executable, str(ROOT / "build_submission.py"),
                "--beat-this-root", str(beat_this), "--casm-root", str(casm),
                "--beatthis-checkpoint", str(weights["beatthis"]),
                "--mscnn-checkpoint", str(weights["mscnn"]),
                "--tcn-checkpoint", str(weights["tcn"]),
                "--output-dir", str(output), "--checkpoint-role", "fixture",
                "--checkpoint-epoch", "119", "--training-run", "fixture",
                "--mirex-task", "beat",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            readme = (output / "README.md").read_text()
            lines = [line for line in readme.splitlines()
                     if line.startswith("./run.sh ") and "%input" in line and "%output" in line]
            self.assertEqual(len(lines), 9)
            self.assertTrue(all("--task beat" in line for line in lines))
            self.assertEqual({line.split("--backbone ")[1].split()[0] for line in lines},
                             {"beatthis", "mscnn", "tcn"})
            self.assertEqual({line.split("--decoder ")[1].split()[0] for line in lines},
                             {"casm", "dbn55_215", "dbn30_300"})
            manifest = json.loads((output / "MANIFEST.json").read_text())
            self.assertEqual(len(manifest["organizer_commands"]["beat"]), 9)
            self.assertEqual(set(manifest["backbones"]), {"beatthis", "mscnn", "tcn"})
            self.assertTrue((output / "weights" / "beatthis_mirex.ckpt").is_file())
            self.assertTrue((output / "weights" / "mscnn_mirex.ckpt").is_file())
            self.assertTrue((output / "weights" / "tcn_mirex.ckpt").is_file())
            self.assertTrue((output / "mirex_pipeline" / "tcn_backend.py").is_file())
            registry = json.loads((output / "config" / "backbones.json").read_text())
            self.assertEqual(set(registry["backbones"]), {"beatthis", "mscnn", "tcn"})
            self.assertIn("train-split", registry["backbones"]["beatthis"]["description"])

    def test_beatfm_bundle_is_self_contained_at_file_contract_level(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            beat_this = base / "beat_this_source"
            (beat_this / "beat_this").mkdir(parents=True)
            (beat_this / "beat_this" / "__init__.py").write_text("")
            casm = base / "casm"
            (casm / "src" / "casm_beat_tracking").mkdir(parents=True)
            (casm / "src" / "casm_beat_tracking" / "__init__.py").write_text("")
            checkpoint = base / "beatthis.ckpt"
            checkpoint.write_bytes(b"beatthis-test")
            beatfm_checkpoint = base / "beatfm.pt"
            beatfm_checkpoint.write_bytes(b"beatfm-test")
            source = base / "beatfm_source"
            source.mkdir()
            for name in ("MultilevelSemanticAggregation.py", "model.py"):
                (source / name).write_text("# fixture\n")
            mert = base / "mert"
            mert.mkdir()
            for name in ("pytorch_model.bin", "config.json", "preprocessor_config.json",
                         "modeling_MERT.py", "configuration_MERT.py"):
                (mert / name).write_bytes(b"fixture")
            output = base / "bundle"
            command = [
                sys.executable, str(ROOT / "build_submission.py"),
                "--beat-this-root", str(beat_this), "--casm-root", str(casm),
                "--beatthis-checkpoint", str(checkpoint),
                "--beatfm-checkpoint", str(beatfm_checkpoint),
                "--beatfm-source-dir", str(source), "--beatfm-mert-dir", str(mert),
                "--output-dir", str(output), "--checkpoint-role", "fixture",
                "--checkpoint-epoch", "1", "--training-run", "fixture",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertTrue((output / "backbone-retrain" / "train_beatfm.py").is_file())
            self.assertTrue((output / "third_party" / "beatfm_source" / "model.py").is_file())
            self.assertTrue((output / "third_party" / "mert_v1_95m" / "pytorch_model.bin").is_file())
            self.assertTrue((output / "requirements-beatfm.txt").is_file())
            registry = json.loads((output / "config" / "backbones.json").read_text())
            self.assertEqual(registry["backbones"]["beatfm"]["status"],
                             "ready-in-bundle-private-assets")
            self.assertEqual(registry["backbones"]["mscnn"]["status"],
                             "checkpoint-not-in-bundle")
            manifest = json.loads((output / "MANIFEST.json").read_text())
            self.assertIn("--task beat", manifest["mirex_commands"]["beat"])
            self.assertIn(
                "--task downbeat", manifest["mirex_commands"]["downbeat"]
            )
            downbeat_output = base / "downbeat_bundle"
            downbeat_command = command.copy()
            downbeat_command[downbeat_command.index(str(output))] = str(downbeat_output)
            downbeat_command.extend(("--mirex-task", "downbeat"))
            subprocess.run(
                downbeat_command, check=True, capture_output=True, text=True
            )
            downbeat_readme = (downbeat_output / "README.md").read_text()
            organizer_lines = [
                line for line in downbeat_readme.splitlines()
                if "%input" in line and "%output" in line
            ]
            self.assertEqual(len(organizer_lines), 4)
            self.assertTrue(all("--task downbeat" in line for line in organizer_lines))
            downbeat_manifest = json.loads(
                (downbeat_output / "MANIFEST.json").read_text()
            )
            self.assertEqual(set(downbeat_manifest["mirex_commands"]), {"downbeat"})

    def test_beatfm_requires_source_and_mert_together(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            checkpoint = base / "beatthis.ckpt"
            checkpoint.write_bytes(b"test")
            command = [
                sys.executable, str(ROOT / "build_submission.py"),
                "--beat-this-root", str(base), "--casm-root", str(base),
                "--beatthis-checkpoint", str(checkpoint),
                "--beatfm-checkpoint", str(checkpoint),
                "--output-dir", str(base / "bundle"), "--checkpoint-role", "fixture",
                "--checkpoint-epoch", "1", "--training-run", "fixture",
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be bundled together", result.stderr)
            self.assertFalse((base / "bundle").exists())


if __name__ == "__main__":
    unittest.main()
