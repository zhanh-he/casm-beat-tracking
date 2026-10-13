"""Run the audited Beat This trainer without its automatic GTZAN test phase.

The upstream script calls ``Trainer.test`` immediately after ``Trainer.fit``.
GTZAN is excluded from MIREX 2026 development, so the test call is disabled
for this full-allowed-data retrain. All model and optimization code remains
the upstream implementation.
"""

from __future__ import annotations

import os
import runpy
from pathlib import Path

from pytorch_lightning import Trainer


def _skip_target_test(self: Trainer, *args: object, **kwargs: object) -> None:
    print("MIREX_TARGET_TEST_SKIPPED: no GTZAN or SMC evaluation", flush=True)


def main() -> None:
    trainer_path = Path(os.environ["BEAT_THIS_ROOT"]) / "launch_scripts" / "train.py"
    if not trainer_path.is_file():
        raise FileNotFoundError(trainer_path)
    Trainer.test = _skip_target_test
    runpy.run_path(str(trainer_path), run_name="__main__")


if __name__ == "__main__":
    main()
