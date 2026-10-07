from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from mirex_pipeline.backbones import load_specs
from mirex_pipeline.cli import _write_events, build_parser, main, resolved_dbn_bpm
from mirex_pipeline.contracts import FrameActivations
from mirex_pipeline.decoders import DirectDecoder


ROOT = Path(__file__).resolve().parent.parent


class PipelineTest(unittest.TestCase):
    def test_backbone_manifest_has_four_named_slots(self) -> None:
        specs = load_specs(ROOT / "config" / "backbones.json")
        self.assertEqual(set(specs), {"beatthis", "mscnn", "tcn", "beatfm"})
        self.assertIsNotNone(specs["beatthis"].adapter)
        self.assertEqual(specs["mscnn"].adapter, specs["beatthis"].adapter)
        self.assertEqual(specs["beatfm"].adapter, "mirex_pipeline.beatfm_backend:BeatFMBackend")
        self.assertEqual(specs["tcn"].adapter, "mirex_pipeline.tcn_backend:TCNBackend")

    def test_dbn_ranges(self) -> None:
        cases = [
            (False, None, (55.0, 215.0)),
            (True, None, (30.0, 300.0)),
            (False, [40.0, 240.0], (40.0, 240.0)),
        ]
        for wide, explicit, expected in cases:
            with self.subTest(wide=wide, explicit=explicit):
                args = argparse.Namespace(dbn_wide=wide, dbn_bpm=explicit)
                self.assertEqual(resolved_dbn_bpm(args), expected)
        parser = build_parser()
        for name, expected in (("dbn55_215", (55.0, 215.0)), ("dbn30_300", (30.0, 300.0))):
            with self.subTest(decoder=name):
                args = parser.parse_args(["--decoder", name, "in.wav", "out.txt"])
                self.assertEqual(resolved_dbn_bpm(args), expected)

    def test_task_defaults_to_beat_and_accepts_downbeat(self) -> None:
        parser = build_parser()
        self.assertEqual(parser.parse_args(["in.wav", "out.txt"]).task, "beat")
        self.assertEqual(
            parser.parse_args(["--task", "downbeat", "in.wav", "out.txt"]).task,
            "downbeat",
        )

    def test_event_writer_supports_downbeat_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "downbeats.txt"
            _write_events(
                output, np.asarray([0.5, 2.5]), event_name="downbeat"
            )
            self.assertEqual(output.read_text(), "0.500000000\n2.500000000\n")

    def test_cli_writes_downbeats_selected_by_task(self) -> None:
        class Backbone:
            def predict(self, _: Path) -> FrameActivations:
                return FrameActivations(np.zeros(3), np.zeros(3), fps=50.0)

        class Decoder:
            def decode(self, _: FrameActivations) -> tuple[np.ndarray, np.ndarray]:
                return np.asarray([0.5, 1.0]), np.asarray([0.5])

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            input_path = base / "input.wav"
            input_path.touch()
            output_path = base / "output.txt"
            with (
                patch("mirex_pipeline.cli.load_backbone", return_value=Backbone()),
                patch("mirex_pipeline.cli.make_decoder", return_value=Decoder()),
            ):
                main(
                    [
                        "--task",
                        "downbeat",
                        "--decoder",
                        "direct",
                        str(input_path),
                        str(output_path),
                    ]
                )
            self.assertEqual(output_path.read_text(), "0.500000000\n")

    def test_direct_decoder_matches_local_maxima_contract(self) -> None:
        beat = np.full(30, -4.0)
        downbeat = np.full(30, -4.0)
        beat[[5, 15, 25]] = 4.0
        downbeat[[5, 25]] = 3.0
        activations = FrameActivations(beat, downbeat, fps=10.0)
        beats, downbeats = DirectDecoder().decode(activations)
        np.testing.assert_allclose(beats, [0.5, 1.5, 2.5])
        np.testing.assert_allclose(downbeats, [0.5, 2.5])

    def test_direct_decoder_preserves_downbeats_if_beats_are_empty(self) -> None:
        beat = np.full(20, -4.0)
        downbeat = np.full(20, -4.0)
        downbeat[[5, 15]] = 3.0
        beats, downbeats = DirectDecoder().decode(
            FrameActivations(beat, downbeat, fps=10.0)
        )
        self.assertEqual(len(beats), 0)
        np.testing.assert_allclose(downbeats, [0.5, 1.5])

    def test_manifest_is_strict_json(self) -> None:
        payload = json.loads((ROOT / "config" / "backbones.json").read_text())
        self.assertEqual(payload["activation_contract"]["fps"], 50.0)


if __name__ == "__main__":
    unittest.main()
