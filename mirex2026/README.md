# CASM MIREX 2026 competition pipeline

This directory is the MIREX-facing inference and packaging workspace within
the single `paper-revision` branch. It is a **competition entry, not a repeat
conference-paper submission**. Our CASM methodology was submitted to ICASSP
2027 as a conference paper, with its experiments in [`../experiments/`](../experiments/).
MIREX applies the method
to competition backbones retrained without SMC or GTZAN in development.
After allowed-validation selection was frozen, the primary BeatThis model was
retrained on all allowed data. Secondary models retain their explicitly
declared data coverage. The two protocols do not share backbone checkpoints.

## Layout

- [`backbone-retrain/`](backbone-retrain/): why and how the backbones are
  retrained for MIREX, including the [BeatFM source/data audit](backbone-retrain/BEATFM_SOURCE_AUDIT.md).
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
| BeatThis | three-seed expanded search, full-allowed retrain, and four-decoder one-WAV smoke complete | primary submission |
| MSCNN | seed-0 epoch 1499 selected on allowed validation; 1,500-epoch full-allowed retrain running on Kaya with an SMC/GTZAN exclusion gate | highest-priority remaining retrain |
| BeatFM | 911-piece epoch-15 checkpoint selected; experiments stopped and artifacts retained | reduced-data fallback only |

## Checkpoint selection and frozen diagnostics

We prepare separate MIREX 2026 entries for **Audio Beat Tracking** and
**Audio Downbeat Estimation**. Both entries use the same joint beat/downbeat
frontends and decoder interface; `--task beat` or `--task downbeat` determines
which event times are written. Beat remains the backward-compatible default.

Checkpoint and training-duration decisions were made only on allowed
validation data. In particular, BeatThis seed 2 epoch 119, MSCNN seed 0 epoch
1499, and TCN seed 0 epoch 119 were frozen before the corresponding all-
allowed-data retrains. GTZAN and SMC were absent from training, calibration,
seed selection, epoch selection, and decoder selection. The table below is a
post-freeze diagnostic record, **not** MIREX model-selection evidence and not
an official MIREX result.

Values are piece-macro percentages. The nine metric columns make both planned
submissions explicit: GTZAN beat F/CMLt/AMLt, GTZAN downbeat F/CMLt/AMLt, and
SMC beat F/CMLt/AMLt. SMC has no downbeat column because the retained SMC
annotations are beat-only. Within a row, each slash separates the two decoders
listed in `Postprocessing`; bold marks the best of the four decoders for that
fixed checkpoint and metric. `—` means not yet measured, never zero. GTZAN
contains 993 valid pieces and SMC contains 217.

| Model weight | Training data | Postprocessing | GTZ beat F | GTZ beat CMLt | GTZ beat AMLt | GTZ downbeat F | GTZ downbeat CMLt | GTZ downbeat AMLt | SMC beat F | SMC beat CMLt | SMC beat AMLt |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BeatThis seed-2 e119 | 3,783 log-Mel; 556 allowed validation | Direct / CASM | 88.96 / **89.00** | 79.64 / 79.86 | 89.66 / 90.07 | **78.05** / 77.75 | 66.52 / 70.98 | 79.79 / 84.86 | 57.75 / **57.99** | 41.74 / 43.34 | 52.30 / 54.68 |
|  |  | DBN 55–215 / DBN 30–300 | 88.36 / 88.50 | **80.98** / 80.49 | 91.61 / **92.23** | 76.99 / 77.39 | 72.55 / **72.61** | 88.20 / **88.56** | 54.59 / 54.66 | 42.27 / **43.38** | 58.25 / **58.43** |
| BeatThis seed-2 e120, full retrain | 4,339 log-Mel; no held-out validation | Direct / CASM | 88.78 / 88.83 | 79.04 / 79.30 | 89.61 / 90.11 | 77.76 / 77.74 | 66.95 / 71.52 | 80.31 / 84.40 | **59.21** / 58.97 | 43.73 / 44.41 | 55.50 / 57.11 |
|  |  | DBN 55–215 / DBN 30–300 | 88.33 / **88.94** | 80.59 / **80.71** | 91.48 / **92.51** | 77.12 / **77.84** | 72.77 / **73.31** | 87.60 / **88.12** | 56.31 / 56.53 | 43.90 / **44.96** | **61.22** / 60.51 |
| MSCNN seed-0 e1499 | 3,783 log-Mel; 556 allowed validation | Direct / CASM | 85.94 / **86.30** | 72.18 / 73.33 | 78.95 / 80.42 | 69.59 / 71.66 | 50.77 / 61.17 | 61.63 / 72.43 | 54.81 / **55.72** | 34.81 / **39.27** | 41.57 / 46.94 |
|  |  | DBN 55–215 / DBN 30–300 | 85.52 / 84.54 | **76.90** / 74.80 | **86.74** / 85.88 | **72.09** / 71.25 | **68.78** / 67.25 | **84.92** / 84.31 | 50.46 / 46.91 | 39.11 / 32.89 | **53.45** / 49.79 |
| MSCNN seed-0 e1500, full retrain running | 4,339 log-Mel; no held-out validation | Direct / CASM | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
| TCN seed-0 e119 | 3,783 log-Mel; 556 allowed validation | Direct / CASM | 86.54 / **86.81** | 72.81 / **73.82** | 80.54 / 81.76 | 61.23 / 65.92 | 21.29 / 51.74 | 59.29 / 70.96 | 51.54 / **51.85** | 27.76 / **30.06** | 33.43 / 37.93 |
|  |  | DBN 55–215 / DBN 30–300 | 84.52 / 83.87 | 73.23 / 71.67 | **86.54** / 86.32 | **66.58** / 65.87 | **59.77** / 58.95 | 82.16 / **82.41** | 42.09 / 36.72 | 22.19 / 15.81 | **39.71** / 36.70 |
| TCN seed-0 e120, full retrain | 4,339 log-Mel; no held-out validation | Direct / CASM | 86.66 / **86.99** | 73.20 / **74.31** | 80.85 / 82.19 | 62.05 / **67.32** | 24.25 / 53.98 | 59.89 / 71.41 | 51.41 / **51.78** | 27.94 / **30.24** | 33.81 / 37.93 |
|  |  | DBN 55–215 / DBN 30–300 | 84.11 / 83.78 | 72.49 / 71.43 | 86.16 / **86.41** | 67.24 / 66.49 | **60.32** / 58.97 | **81.96** / 81.67 | 41.25 / 37.59 | 21.16 / 15.51 | 37.64 / **38.05** |
| BeatFM e15, stopped | 911 mapped WAVs: 774 train + 137 validation | Direct / CASM | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
| BeatFM expanded, stopped | 1,684 mapped WAVs: 1,431 train + 253 validation | Direct / CASM | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
| SpecTNT placeholder | not implemented | Direct / CASM | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |

The source table, checkpoint hashes, and per-piece artifacts are retained in
[`results/MODEL_DECODER_MATRIX_20261005.md`](results/MODEL_DECODER_MATRIX_20261005.md)
and [`results/target_table_20261005/`](results/target_table_20261005/). The
upstream BeatThis `final0` checkpoint is deliberately absent because it was
trained on SMC folds and therefore cannot be evaluated on full SMC here.

The BeatThis fork's audited `Audio2Frames` loader reads checkpoint architecture
metadata and supports both BeatThis and MSCNN. BeatFM has a separate
frozen-MERT adapter. A private self-contained bundle includes the audited
BeatFM source and pinned MERT files; the repository runtime instead accepts
`BEATFM_SOURCE_DIR` and `BEATFM_MERT_DIR`. Its one-epoch pilot weight is
explicitly refused for ordinary submission inference. The full BeatThis-data
comparison remains blocked by missing original audio. The 911- and
1,684-piece candidates are labeled as reduced-data experiments.

| Decoder | Default tempo range | Notes |
|---|---:|---|
| `direct` | unconstrained | BeatThis-compatible seven-frame local-max peak picking |
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
./run.sh --task downbeat --backbone beatthis --decoder casm %input %output

./run.sh --backbone mscnn --decoder casm %input %output
./run.sh --backbone beatfm --decoder casm %input %output
```

`%input` is one WAV file and `%output` is the full path of an ASCII file with
one selected beat or downbeat time in seconds per line. The frontend
downmixes/resamples inputs when necessary. `--list-backbones` prints the
current integration status.

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

The private final archive is built with `build_submission.py`. It copies only
supplied checkpoints, vendors the audited BeatThis and CASM sources, includes
BeatFM/MERT only when explicitly supplied, and records SHA-256 hashes in
`MANIFEST.json`. Check [third-party rights](THIRD_PARTY.md) before any external
distribution. Its concise
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
- Clean selection is frozen on allowed validation data. The [2026 rules](https://music-ir.org/mirex/wiki/2026:Audio_Beat_Tracking)
  prohibit SMC and GTZAN for any development purpose; earlier target-set
  screens are historical artifacts, not a permitted MIREX diagnostic loop.
- After seed/epoch selection, BeatThis was retrained on all allowed training
  and validation pieces with the fixed recipe. The equivalent MSCNN full-data
  retrain is now running; the packaged MSCNN weight remains the disclosed
  train-split checkpoint until that retrain completes and passes smoke tests.
  BeatFM remains a stopped, reduced-data train-split experiment.
- The final README submitted to MIREX will contain only the command lines that
  we actually want the organizers to execute; examples above are capability
  documentation, not a request to evaluate every Cartesian-product variant.

## Contact

Zhanh He — project contact via
[github.com/zhanh-he/casm-beat-tracking](https://github.com/zhanh-he/casm-beat-tracking).
