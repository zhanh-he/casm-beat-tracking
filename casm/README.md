# CASM package

This directory contains everything needed to install, use, and validate CASM:

- `src/casm_beat_tracking/`: decoder, processors, and CLI.
- `config/`: human-readable frozen 7F configuration.
- `src/casm_beat_tracking/data/`: the same configuration bundled inside the
  Python package for zero-setup inference.
- `tests/`: unit and evaluation tests.
- `benchmarks/`: local throughput benchmark.
- `docs/`: API and calibration documentation.

CASM itself has no learned neural weights. Its inference "weights" are the
frozen scalar configuration bundled with the package, so `CASMDecoder()` works
immediately after installation. BeatThis, MSCNN, and TCN checkpoint binaries
belong to the activation backbones. Their filenames and availability are
documented in the [inference weight inventory](../mirex2026/weights/README.md),
and downloads are provided through [GitHub Releases](https://github.com/zhanh-he/casm-beat-tracking/releases).
