# CASM MIREX 2026 competition pipeline

This directory is the MIREX-facing inference and packaging workspace within
the single `paper-revision` branch. It is a **competition entry, not a repeat
conference-paper submission**. Our CASM methodology was submitted to ICASSP
2027 as a conference paper, with its experiments in [`../experiments/`](../experiments/).
MIREX applies the method
to competition backbones retrained without SMC or GTZAN in development.
After allowed-validation selection is frozen, the chosen model is to be
retrained on all remaining allowed data. The two protocols do not share
backbone checkpoints.

## Layout

- [`backbone-retrain/`](backbone-retrain/): why and how BeatThis/other backbones
  are retrained for MIREX; current training script and pending final recipe.
- [`scripts/`](scripts/): provenance-gated evaluation and result rebuild tools.
- [`results/`](results/): corrected diagnostics and result tables, clearly
  separate from final official MIREX scores.
- `mirex_pipeline/`, `config/`, and the root `run.sh`/`install.sh`: runtime
  adapters, decoder choices, and packaging entry points.

## Supported matrix

Every backbone must produce finite, one-dimensional beat and downbeat logits
at 50 Hz. The shared decoder layer then applies the requested postprocessor.

| Backbone | Status | MIREX role |
|---|---|---|
| BeatThis | adapter ready; final checkpoint pending | primary submission |
| MSCNN | shared adapter verified; seed-0 training in progress | lightweight secondary |
| BeatFM | source revision, adapter, and checkpoint pending | next primary candidate |

The BeatThis fork's audited `Audio2Frames` loader reads checkpoint architecture
metadata and supports both BeatThis and MSCNN. BeatFM remains a deliberate,
disabled integration slot in `config/backbones.json`; it fails with an explicit
message until its audited source and weights are supplied.

| Decoder | Default tempo range | Notes |
|---|---:|---|
| `direct` | unconstrained | BeatThis-compatible 70 ms local-max peak picking |
| `dbn` | 55–215 BPM | joint madmom beat/downbeat DBN |
| `casm` | 30–300 BPM | frozen no-SMC global CASM configuration |

The exploratory wide-DBN setting is exposed as `--dbn-wide`, equivalent to
`--dbn-bpm 30 300`.

## One-file interface

The default is BeatThis + CASM:

```text
./run.sh %input %output
```

All combinations use the same entry point:

```text
./run.sh --backbone beatthis --decoder direct %input %output
./run.sh --backbone beatthis --decoder dbn %input %output
./run.sh --backbone beatthis --decoder dbn --dbn-wide %input %output
./run.sh --backbone beatthis --decoder casm %input %output

./run.sh --backbone mscnn --decoder casm %input %output
./run.sh --backbone beatfm --decoder casm %input %output
```

`%input` is one WAV file and `%output` is the full path of an ASCII file with
one beat time in seconds per line. The frontend downmixes/resamples inputs when
necessary. `--list-backbones` prints the current integration status.

## Installation

Use Python 3.11. The installer creates an isolated environment, installs the
core runtime, and installs the exact Git revision of madmom used for DBN
experiments:

```text
./install.sh
PYTHON=.venv/bin/python ./run.sh --backbone beatthis --decoder casm %input %output
```

The container path exposes the identical CLI:

```text
docker build -t casm-mirex-2026 .
docker run --rm --gpus all \
  -v /absolute/input:/input:ro -v /absolute/output:/output \
  casm-mirex-2026 \
  --backbone beatthis --decoder casm \
  /input/example.wav /output/example.txt
```

The final archive is built with `build_submission.py`. It copies only supplied
checkpoints, vendors the audited BeatThis and CASM sources, and records SHA-256
hashes in `MANIFEST.json`. Its concise
[`SUBMISSION_README.md`](SUBMISSION_README.md) is copied as the bundle README;
the development links in this file are not placed into the standalone archive.

## Experiment and submission policy

- Every evaluation must pass the [training/evaluation disjointness guard](scripts/README.md).
  The official BeatThis `final0` includes SMC in training and is never scored
  on SMC in this pipeline.
- SMC and GTZAN are absent from MIREX backbone training, validation, seed
  selection, checkpoint selection, and the competition CASM configuration's
  calibration. That configuration is
  [`config/casm-no-smc.json`](config/casm-no-smc.json), **not** the paper's
  published 7F default (which did use SMC for calibration).
- Clean selection is frozen on allowed validation data before target
  diagnostics are generated.
- Target-oracle tables, when produced for internal diagnosis, are labeled
  ineligible for the MIREX submission.
- After seed/epoch selection, the winning backbone is retrained on all allowed
  training and validation pieces with the fixed recipe.
- The final README submitted to MIREX will contain only the command lines that
  we actually want the organizers to execute; examples above are capability
  documentation, not a request to evaluate every Cartesian-product variant.

## Contact

Zhanh He — project contact via
[github.com/zhanh-he/casm-beat-tracking](https://github.com/zhanh-he/casm-beat-tracking).
