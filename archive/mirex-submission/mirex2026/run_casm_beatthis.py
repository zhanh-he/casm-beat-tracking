#!/usr/bin/env python3
"""Compatibility wrapper for the original BeatThis + CASM entry point."""

from __future__ import annotations

import sys

from mirex_pipeline.cli import main


if __name__ == "__main__":
    main(["--backbone", "beatthis", "--decoder", "casm", *sys.argv[1:]])
