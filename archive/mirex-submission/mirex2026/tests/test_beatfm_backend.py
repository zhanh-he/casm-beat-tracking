from __future__ import annotations

import unittest

import numpy as np

from mirex_pipeline.beatfm_backend import merge_clip_logits, resample_logits


class BeatFMBackendMathTest(unittest.TestCase):
    def test_overlapping_clip_logits_are_averaged(self) -> None:
        beat, downbeat = merge_clip_logits([
            (0, np.full(5, 2.0), np.full(5, 4.0)),
            (3, np.full(5, 6.0), np.full(5, 8.0)),
        ], 8)
        np.testing.assert_array_equal(beat, [2, 2, 2, 4, 4, 6, 6, 6])
        np.testing.assert_array_equal(downbeat, [4, 4, 4, 6, 6, 8, 8, 8])

    def test_missing_frame_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "uncovered"):
            merge_clip_logits([(0, np.ones(2), np.ones(2))], 3)

    def test_75_to_50_preserves_frame_time(self) -> None:
        source = np.arange(75, dtype=np.float64) / 75.0
        target = resample_logits(source, 75.0, 50.0, 1.0)
        self.assertEqual(len(target), 50)
        np.testing.assert_allclose(target, np.arange(50) / 50.0, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
