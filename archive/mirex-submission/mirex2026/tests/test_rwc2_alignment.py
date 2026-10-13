from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "backbone-retrain" / "rwc2_audio_map.py"
SPEC = importlib.util.spec_from_file_location("rwc2_audio_map", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class RWC2AlignmentTest(unittest.TestCase):
    def test_half_time_labels_match_same_recording(self) -> None:
        official = [(float(i), i % 4 + 1) for i in range(100)]
        old = official[::2]
        aligned = module.align_beat_times(old, official)
        self.assertEqual(aligned.shift_seconds, 0)
        self.assertEqual(aligned.within_1ms, len(old))
        self.assertEqual(aligned.reference_density_difference, 50)

    def test_constant_release_offset_is_detected(self) -> None:
        official = [(float(i), i % 4 + 1) for i in range(100)]
        old = [(time + .218, meter) for time, meter in official]
        aligned = module.align_beat_times(old, official)
        self.assertAlmostEqual(aligned.shift_seconds, -.218)
        self.assertEqual(aligned.within_1ms, 100)

    def test_unrelated_timing_rejected(self) -> None:
        official = [(float(i), 1) for i in range(100)]
        old = [(time + .3 + .02 * i, 1) for i, (time, _) in enumerate(official)]
        with self.assertRaisesRegex(ValueError, "timing mismatch"):
            module.align_beat_times(old, official)


if __name__ == "__main__":
    unittest.main()
