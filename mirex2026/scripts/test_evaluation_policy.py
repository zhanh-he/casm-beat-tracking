from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evaluation_policy import assert_disjoint_pieces, eligible_datasets, load_models


class EvaluationPolicyTest(unittest.TestCase):
    def test_official_final0_cannot_be_scored_on_smc(self) -> None:
        model = {
            "model_id": "official_final0",
            "checkpoint": "/checkpoints/beat_this-final0.ckpt",
            "smc_training_status": "included_upstream_final0",
        }
        self.assertEqual(eligible_datasets(model), ("gtzan",))
        model["smc_training_status"] = "excluded"
        with self.assertRaisesRegex(ValueError, "must declare SMC"):
            eligible_datasets(model)

    def test_unknown_provenance_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown training provenance"):
            eligible_datasets(
                {
                    "model_id": "unknown",
                    "checkpoint": "/checkpoints/unknown.ckpt",
                    "smc_training_status": "unknown",
                }
            )

    def test_piece_overlap_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "training/evaluation overlap"):
            assert_disjoint_pieces(
                {"smc/001", "smc/002"}, {"smc/002"}, context="fold0"
            )

    def test_manifest_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "models.tsv"
            path.write_text(
                "model_id\tcheckpoint\tsmc_training_status\n"
                "official_final0\t/checkpoints/beat_this-final0.ckpt\t"
                "included_upstream_final0\n"
                "ours\t/checkpoints/ours.ckpt\texcluded\n"
            )
            models = load_models(path)
            self.assertEqual([eligible_datasets(row) for row in models], [
                ("gtzan",), ("smc", "gtzan")
            ])


if __name__ == "__main__":
    unittest.main()
