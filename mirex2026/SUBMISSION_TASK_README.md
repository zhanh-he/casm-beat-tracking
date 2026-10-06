# CASM MIREX 2026 @TASK_TITLE@

This package is an inference entry for the @TASK_TITLE@ task. It is not a
repeat submission of our ICASSP 2027 paper, which presents the CASM
postprocessing methodology. The BeatThis backbone and log-Mel preprocessing
originate from the upstream CPJKU Beat This project. Our competition weight
was retrained for 120 epochs on 4,339 allowed BeatThis log-Mel pieces using
seed 2, after seed and duration selection on a separate 556-piece allowed
validation split. SMC and GTZAN were excluded from training, validation,
calibration, and all competition model/decoder decisions.

The input is one 44.1 kHz, 16-bit mono WAV. The output is an ASCII text file
with one @EVENT@ time in seconds per line. The entry accepts the complete
input and output paths. Target OS is Linux x86_64; the extracted source bundle
was smoke-tested on Ubuntu 22.04.5 LTS. Install Python 3.11, then run
`./install.sh` once in the extracted directory. It creates an isolated
`.venv` and installs pinned dependencies. An NVIDIA GPU is recommended;
the program also has a CPU fallback.

The following are the organizer evaluation commands for this task only.
Each command uses the same BeatThis weight. Direct is the original local-peak
decoder, DBN uses a 55–215 BPM default or exploratory 30–300 BPM range, and
CASM uses the frozen no-SMC configuration at 30–300 BPM.

```text
PYTHON=.venv/bin/python ./run.sh --task @TASK@ --backbone beatthis --decoder casm %input %output
PYTHON=.venv/bin/python ./run.sh --task @TASK@ --backbone beatthis --decoder direct %input %output
PYTHON=.venv/bin/python ./run.sh --task @TASK@ --backbone beatthis --decoder dbn %input %output
PYTHON=.venv/bin/python ./run.sh --task @TASK@ --backbone beatthis --decoder dbn --dbn-wide %input %output
```

An MSCNN train-split checkpoint is also present as a disclosed secondary
research candidate. Its 4,339-piece full retrain is not included here and no
MSCNN organizer command is requested in this README. BeatFM assets are not
included. The manifest lists every file's SHA-256 and the exact checkpoint
identities. See `SYSTEM_DESCRIPTION.md` and `THIRD_PARTY.md` for methodology
and source/license details.

Contact: Zhanh He, via the
[CASM repository](https://github.com/zhanh-he/casm-beat-tracking/issues).
