# CASM MIREX 2026 Audio Beat Tracking system

This is a competition inference bundle, not a resubmission of our ICASSP
paper. That paper presents the CASM postprocessing methodology; this bundle
combines a separately retrained BeatThis backbone with selectable Direct,
DBN, or CASM decoding. The BeatThis architecture and preprocessing originate
from the upstream CPJKU Beat This project.

Target OS: Linux x86_64 (runtime smoke-tested on Ubuntu 22.04.5 LTS with an
NVIDIA GPU). A `Dockerfile` is also provided. Install with Python 3.11 by
running `./install.sh`, which creates an isolated `.venv` and installs the
pinned Python/DBN dependencies. The clean-machine installation itself still
requires organizer-side verification; the one-WAV commands below have been
smoke-tested on the stated Linux host. Run one 44.1 kHz, 16-bit mono WAV at
a time. The exact MIREX command lines are:

```text
PYTHON=.venv/bin/python ./run.sh --backbone beatthis --decoder casm %input %output
PYTHON=.venv/bin/python ./run.sh --backbone beatthis --decoder direct %input %output
PYTHON=.venv/bin/python ./run.sh --backbone beatthis --decoder dbn %input %output
PYTHON=.venv/bin/python ./run.sh --backbone beatthis --decoder dbn --dbn-wide %input %output
```

Each output contains one beat time in seconds per line. DBN defaults to
55–215 BPM; `--dbn-wide` selects the exploratory 30–300 BPM range. CASM uses
the frozen no-SMC competition configuration at 30–300 BPM. To run an MSCNN
or BeatFM variant when its checkpoint is included, replace `beatthis` with
`mscnn` or `beatfm` in the command above. `--list-backbones` identifies which
models are actually present; an absent checkpoint is not silently replaced.

BeatFM requires its separately supplied BeatFM source and pinned MERT-v1-95M
snapshot. They are included only in private bundles built with explicit
`--beatfm-source-dir` and `--beatfm-mert-dir`; do not publish those assets
without checking their redistribution terms.
See `THIRD_PARTY.md` for MERT's CC BY-NC 4.0 attribution and the unresolved
BeatFM-source redistribution restriction.

The bundle's `MANIFEST.json` records copied checkpoint, configuration, and
source hashes. Use only final frozen checkpoint bundles for an official
submission; development diagnostics in the repository are not official
MIREX results.

Project contact: [zhanh-he/casm-beat-tracking](https://github.com/zhanh-he/casm-beat-tracking/issues).
