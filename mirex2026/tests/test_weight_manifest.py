"""Check the three public MIREX inference exports against their provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WeightManifestTest(unittest.TestCase):
    def test_public_mirex_weights(self) -> None:
        weights = ROOT / "weights"
        records = json.loads((weights / "manifest.json").read_text())["checkpoints"]
        self.assertEqual(set(records), {"beatthis", "mscnn", "tcn"})
        for model, record in records.items():
            with self.subTest(model=model):
                path = weights / record["file"]
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, record["bytes"])
                digest = hashlib.sha256()
                with path.open("rb") as handle:
                    for block in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(block)
                self.assertEqual(digest.hexdigest(), record["sha256"])
                self.assertLess(path.stat().st_size, 100 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
