"""Keep the displayed Direct-baseline table tied to frozen result CSVs."""

from __future__ import annotations

from pathlib import Path
import unittest

from scripts.build_decoder_delta_table import build_table, load_rows, render_cell


ROOT = Path(__file__).resolve().parents[1]


class DecoderDeltaTableTest(unittest.TestCase):
    def test_main_readme_matches_frozen_source_rebuild(self) -> None:
        table = build_table()
        self.assertIn(table, (ROOT / "README.md").read_text())
        self.assertEqual(table.count("| Direct (absolute) |"), 5)
        self.assertEqual(table.count("| CASM Δ |"), 5)
        self.assertEqual(table.count("| PLPDP Δ |"), 5)

    def test_representative_percentage_point_differences(self) -> None:
        rows = load_rows()
        self.assertEqual(
            render_cell(
                rows, "winner_no_smc_final", "gtzan",
                ("beat_fmeasure", "beat_cmlt", "beat_amlt"), "casm_no_smc",
            ),
            "+0.05 / +0.26 / +0.50",
        )
        self.assertEqual(
            render_cell(
                rows, "tcn_split_seed0_e119", "gtzan",
                ("downbeat_fmeasure", "downbeat_cmlt", "downbeat_amlt"),
                "casm_no_smc",
            ),
            "+4.69 / +30.45 / +11.67",
        )


if __name__ == "__main__":
    unittest.main()
