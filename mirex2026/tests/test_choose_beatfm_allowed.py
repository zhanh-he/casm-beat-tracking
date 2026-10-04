"""Synthetic-panel checks for the frozen BeatFM allowed-data selector."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "choose_beatfm_allowed.py"
CANDIDATES = ("best_val_loss", "epoch_0005", "epoch_0010", "epoch_0015", "epoch_0020")
METHODS = ("direct", "casm_30_300", "dbn_55_215", "dbn_30_300")
METRICS = ("beat_f", "beat_cmlt", "beat_amlt", "downbeat_f", "downbeat_cmlt", "downbeat_amlt")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class ChooseBeatFMAllowedTest(unittest.TestCase):
    def test_selects_direct_on_identical_allowed_panel(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "COMPLETE").write_text("done\n")
            provenance = {
                "role": "allowed-validation candidate screen; not MIREX test",
                "validation_pieces": 137,
                "datasets": ["ballroom", "rwc"],
                "checkpoint_candidates": [
                    {"name": name, "sha256": f"hash-{name}", "epoch": index * 5}
                    for index, name in enumerate(CANDIDATES)
                ],
            }
            (root / "provenance.json").write_text(json.dumps(provenance))
            pieces = []
            summaries = []
            for index, name in enumerate(CANDIDATES):
                for method in METHODS:
                    value = 0.5 + (0.01 * index if method == "direct" else 0.0)
                    values = {metric: value for metric in METRICS}
                    for piece in range(137):
                        pieces.append({"candidate": name, "method": method,
                                       "checkpoint_sha256": f"hash-{name}",
                                       "dataset": "ballroom" if piece < 103 else "rwc",
                                       "stem": f"piece-{piece:03d}", **values})
                    summaries.append({"candidate": name, "method": method,
                                      "dataset": "all", "pieces": 137, **values})
            write_csv(root / "pieces.csv", pieces)
            write_csv(root / "summary.csv", summaries)
            selection_path = root / "selection.json"
            result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root),
                                     "--output", str(selection_path)], capture_output=True,
                                    text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            choice = json.loads(selection_path.read_text())
            self.assertEqual(choice["selected_candidate"], "epoch_0020")
            self.assertEqual(choice["panel_piece_count"], 137)
            self.assertEqual(choice["target_datasets_used"], [])


if __name__ == "__main__":
    unittest.main()
