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
| MSCNN | seed-0 epoch 1499 selected on allowed validation; 1,500-epoch full-allowed retrain submitted with an SMC/GTZAN exclusion gate | highest-priority remaining retrain |
| BeatFM | 911-piece epoch-15 checkpoint selected; experiments stopped and artifacts retained | reduced-data fallback only |

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
