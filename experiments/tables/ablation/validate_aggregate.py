"""Fail closed on ablation panel names/counts; not a piece-level provenance proof."""

import csv
from collections import Counter
from pathlib import Path


EXPECTED = {
    "bt_gtzan_seed0": 993,
    "bt_smc_oof": 217,
    "mscnn_gtzan": 993,
    "mscnn_smc_oof": 217,
}
METHODS = {
    "casm_full", "dbn_default", "dbn_matched_30_300", "direct",
    "local_target_fixed", "no_safeguard", "one_sided", "plpdp",
    "strength_only", "width_only",
}


def validate(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    actual = Counter()
    for row in rows:
        panel = row["panel"]
        if panel not in EXPECTED:
            raise ValueError(f"unapproved ablation panel: {panel}")
        if int(row["piece_count"]) != EXPECTED[panel]:
            raise ValueError(f"unexpected piece count for {panel}")
        key = (panel, row["method"])
        if row["method"] not in METHODS or actual[key]:
            raise ValueError(f"unexpected or duplicate method: {key}")
        actual[key] += 1
    expected = {(panel, method) for panel in EXPECTED for method in METHODS}
    if set(actual) != expected:
        raise ValueError(f"missing ablation rows: {sorted(expected - set(actual))}")


if __name__ == "__main__":
    validate(Path(__file__).with_name("aggregate_metrics.csv"))
    print("Ablation aggregate panel allowlist and row counts: OK")
