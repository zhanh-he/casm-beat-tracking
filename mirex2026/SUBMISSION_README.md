# CASM MIREX 2026 Audio Beat Tracking system

This is a competition inference bundle, not a resubmission of our ICASSP
paper. That paper presents the CASM postprocessing methodology; this bundle
combines a separately retrained BeatThis backbone with selectable Direct,
DBN, or CASM decoding. The BeatThis architecture and preprocessing originate
from the upstream CPJKU Beat This project.

Install with Python 3.11 by running `./install.sh`. Run one WAV at a time:

```text
PYTHON=.venv/bin/python ./run.sh --backbone beatthis --decoder casm input.wav output.txt
```

`output.txt` contains one beat time in seconds per line. Other supported
decoder flags are `--decoder direct`, `--decoder dbn` (55–215 BPM), and
`--decoder dbn --dbn-wide` (30–300 BPM). CASM uses the frozen no-SMC
competition configuration with a 30–300 BPM range. `--list-backbones`
reports the adapters actually enabled in this bundle; a named model without
an audited adapter remains unavailable.

The bundle's `MANIFEST.json` records copied checkpoint, configuration, and
source hashes. Use only final frozen checkpoint bundles for an official
submission; development diagnostics in the repository are not official
MIREX results.
