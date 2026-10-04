from __future__ import annotations

import argparse
import json
from pathlib import Path
import unittest

import numpy as np

from mirex_pipeline.backbones import load_specs
from mirex_pipeline.cli import resolved_dbn_bpm
from mirex_pipeline.contracts import FrameActivations
from mirex_pipeline.decoders import DirectDecoder


ROOT = Path(__file__).resolve().parent.parent


class PipelineTest(unittest.TestCase):
    def test_backbone_manifest_has_three_named_slots(self) -> None:
        specs = load_specs(ROOT / "config" / "backbones.json")
        self.assertEqual(set(specs), {"beatthis", "mscnn", "beatfm"})
        self.assertIsNotNone(specs["beatthis"].adapter)
        self.assertEqual(specs["mscnn"].adapter, specs["beatthis"].adapter)
        self.assertEqual(specs["beatfm"].adapter, "mirex_pipeline.beatfm_backend:BeatFMBackend")

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
