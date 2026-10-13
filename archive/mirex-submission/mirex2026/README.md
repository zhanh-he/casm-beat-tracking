# CASM MIREX 2026 competition pipeline

This directory is the MIREX-facing inference and packaging workspace within
the `mirex_submission` branch. It is a **competition entry, not a repeat
conference-paper submission**. Our CASM methodology was submitted to ICASSP
2027 as a conference paper, with its experiments in [`../experiments/`](../experiments/).
MIREX applies the method
to competition backbones retrained without SMC or GTZAN in development.
After allowed-validation selection was frozen, the primary BeatThis model was
retrained on all allowed data. Secondary models retain their explicitly
declared data coverage. The two protocols do not share backbone checkpoints.
The separate 2026-10-07 three-backbone submission candidates deliberately
package the **allowed-validation-selected split weights** for BeatThis,
MSCNN, and TCN, not BeatThis's later full-data retrain.
The repository tracks their [lossless, trainer-stripped `_mirex.ckpt` exports](weights/README.md)
directly; the original Lightning training checkpoints remain private.

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
| BeatThis | three-seed expanded search and separate full-allowed retrain complete | primary; 2026-10-07 bundle uses split weight |
| MSCNN | seed-0 epoch 1499 selected on allowed validation | 2026-10-07 bundle uses split weight |
| TCN | seed-0 epoch 119 selected on allowed validation; 18-way Linux runtime smoke complete | 2026-10-07 bundle uses split weight |
| BeatFM | 911-piece epoch-15 checkpoint selected; experiments stopped and artifacts retained | not in three-backbone bundle |

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

Values are piece-macro percentages. For each fixed model weight, Direct gives the absolute baseline; CASM, both DBN settings, and released-default PLPDP give signed **percentage-point changes (Δ)** from that Direct result. Each metric cell reads **F / CMLt / AMLt**. Positive is better, and bold marks the best of the five decoders for each metric. `—` means unmeasured, not zero. GTZAN has 993 valid pieces; SMC has 217 beat-only pieces. The [original nine-column absolute-score table](results/absolute-score-table/README.md) is preserved separately. PLPDP's 50-to-100-fps adapter and pinned source are documented in [`results/plpdp_default_20261007/`](results/plpdp_default_20261007/).

| Model weight | Training data | Decoder | GTZAN beat F / CMLt / AMLt | GTZAN downbeat F / CMLt / AMLt | SMC beat F / CMLt / AMLt |
|---|---|---|---:|---:|---:|
| BeatThis seed-2 e119 | 3,783 log-Mel; 556 allowed validation | Direct (absolute) | 88.96 / 79.64 / 89.66 | **78.05** / 66.52 / 79.79 | 57.75 / 41.74 / 52.30 |
|  |  | CASM Δ | +0.04 / +0.22 / +0.41 | -0.30 / +4.46 / +5.07 | +0.24 / +1.60 / +2.38 |
|  |  | DBN 55–215 Δ | -0.60 / **+1.34** / +1.95 | -1.06 / +6.03 / +8.41 | -3.16 / +0.53 / +5.95 |
|  |  | DBN 30–300 Δ | -0.46 / +0.85 / **+2.57** | -0.66 / **+6.09** / **+8.77** | -3.09 / **+1.64** / **+6.13** |
|  |  | PLPDP Δ | **+0.06** / +0.36 / -0.05 | -0.04 / +0.13 / +0.08 | **+0.30** / -0.02 / +1.16 |
| BeatThis seed-2 e120, full retrain | 4,339 log-Mel; no held-out validation | Direct (absolute) | 88.78 / 79.04 / 89.61 | 77.76 / 66.95 / 80.31 | **59.21** / 43.73 / 55.50 |
|  |  | CASM Δ | +0.05 / +0.26 / +0.50 | -0.02 / +4.57 / +4.09 | -0.24 / +0.68 / +1.61 |
|  |  | DBN 55–215 Δ | -0.45 / +1.55 / +1.87 | -0.64 / +5.82 / +7.29 | -2.90 / +0.17 / **+5.72** |
|  |  | DBN 30–300 Δ | **+0.16** / **+1.67** / **+2.90** | **+0.08** / **+6.36** / **+7.81** | -2.68 / **+1.23** / +5.01 |
|  |  | PLPDP Δ | +0.08 / +0.49 / +0.08 | +0.06 / +0.32 / +0.20 | -0.30 / -1.54 / +1.80 |
| MSCNN seed-0 e1499 | 3,783 log-Mel; 556 allowed validation | Direct (absolute) | 85.94 / 72.18 / 78.95 | 69.59 / 50.77 / 61.63 | 54.81 / 34.81 / 41.57 |
|  |  | CASM Δ | +0.36 / +1.15 / +1.47 | +2.07 / +10.40 / +10.80 | +0.91 / **+4.46** / +5.37 |
|  |  | DBN 55–215 Δ | -0.42 / **+4.72** / **+7.79** | **+2.50** / **+18.01** / **+23.29** | -4.35 / +4.30 / **+11.88** |
|  |  | DBN 30–300 Δ | -1.40 / +2.62 / +6.93 | +1.66 / +16.48 / +22.68 | -7.90 / -1.92 / +8.22 |
|  |  | PLPDP Δ | **+0.59** / +3.16 / +2.57 | +0.15 / +0.82 / +0.76 | **+1.15** / +3.10 / +6.06 |
| TCN seed-0 e119 | 3,783 log-Mel; 556 allowed validation | Direct (absolute) | 86.54 / 72.81 / 80.54 | 61.23 / 21.29 / 59.29 | 51.54 / 27.76 / 33.43 |
|  |  | CASM Δ | **+0.27** / **+1.01** / +1.22 | +4.69 / +30.45 / +11.67 | **+0.31** / **+2.30** / +4.50 |
|  |  | DBN 55–215 Δ | -2.02 / +0.42 / **+6.00** | **+5.35** / **+38.48** / +22.87 | -9.45 / -5.57 / **+6.28** |
|  |  | DBN 30–300 Δ | -2.67 / -1.14 / +5.78 | +4.64 / +37.66 / **+23.12** | -14.82 / -11.95 / +3.27 |
|  |  | PLPDP Δ | -0.17 / +0.07 / +2.68 | +0.12 / +0.04 / +0.22 | -1.36 / -5.45 / +5.98 |
| TCN seed-0 e120, full retrain | 4,339 log-Mel; no held-out validation | Direct (absolute) | 86.66 / 73.20 / 80.85 | 62.05 / 24.25 / 59.89 | 51.41 / 27.94 / 33.81 |
|  |  | CASM Δ | **+0.33** / **+1.11** / +1.34 | **+5.27** / +29.73 / +11.52 | **+0.37** / **+2.30** / +4.12 |
|  |  | DBN 55–215 Δ | -2.55 / -0.71 / +5.31 | +5.19 / **+36.07** / **+22.07** | -10.16 / -6.78 / +3.83 |
|  |  | DBN 30–300 Δ | -2.88 / -1.77 / **+5.56** | +4.44 / +34.72 / +21.78 | -13.82 / -12.43 / +4.24 |
|  |  | PLPDP Δ | -0.25 / +0.03 / +2.55 | +0.11 / +0.06 / +0.26 | -0.81 / -4.18 / **+6.03** |
| MSCNN seed-0 e1500, full retrain incomplete | 4,339 log-Mel; no held-out validation | — | — | — | — |
| BeatFM e15, stopped | 911 mapped WAVs: 774 train + 137 validation | — | — | — | — |
| BeatFM expanded, stopped | 1,684 mapped WAVs: 1,431 train + 253 validation | — | — | — | — |
| SpecTNT placeholder | not implemented | — | — | — | — |

The source table, checkpoint hashes, and per-piece artifacts are retained in
[`results/MODEL_DECODER_MATRIX_20261005.md`](results/MODEL_DECODER_MATRIX_20261005.md)
and [`results/target_table_20261005/`](results/target_table_20261005/), with
the additional PLPDP piece-level source under
[`results/plpdp_default_20261007/`](results/plpdp_default_20261007/). The
upstream BeatThis `final0` checkpoint is deliberately absent because it was
trained on SMC folds and therefore cannot be evaluated on full SMC here.
The [2026-10-06 recovery inventory](results/EXPERIMENT_RECOVERY_20261006.md)
records live job states, verified hashes, and which missing cells remain blank.

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
| `plpdp` | 30–300 BPM | released default; 50-to-100-fps interpolation before decoding |

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
./run.sh --backbone beatthis --decoder plpdp %input %output
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
supplied checkpoints, vendors the audited BeatThis, CASM, and released-default
PLPDP sources for the three-backbone matrix, includes
BeatFM/MERT only when explicitly supplied, and records SHA-256 hashes in
`MANIFEST.json`. For an actual task submission, use `--mirex-task beat` or
`--mirex-task downbeat`: each generates a README with only that task's
organizer command lines from [`SUBMISSION_TASK_MATRIX_README.md`](SUBMISSION_TASK_MATRIX_README.md)
for the three-backbone package. The older single-backbone template is
[`SUBMISSION_TASK_README.md`](SUBMISSION_TASK_README.md).
The generic dual-task README is for internal smoke tests only, because MIREX
automatically evaluates every README line containing both input and output
placeholders. The earlier three-decoder archive record remains in
[`SUBMISSION_HANDOFF_20261007.md`](SUBMISSION_HANDOFF_20261007.md); current
PLPDP-enabled archive names, hashes, and technical QA are in
[`SUBMISSION_HANDOFF_PLPDP_20261007.md`](SUBMISSION_HANDOFF_PLPDP_20261007.md). Check
[third-party rights](THIRD_PARTY.md) before any external distribution.

The 2026-10-07 three-backbone package uses
[`SUBMISSION_TASK_MATRIX_README.md`](SUBMISSION_TASK_MATRIX_README.md), with
exactly twelve organizer lines per task: BeatThis/MSCNN/TCN ×
CASM/DBN55–215/DBN30–300/PLPDP. Its BeatThis checkpoint is the split seed-2
epoch-119 weight, not the later 4,339-piece full retrain. The smaller
task-specific archives and their verified hashes are listed in the
[current submission handoff](SUBMISSION_HANDOFF_PLPDP_20261007.md).

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
- After seed/epoch selection, BeatThis was separately retrained on all allowed
  training and validation pieces with the fixed recipe. That different weight
  is **not** in the 2026-10-07 three-backbone split-weight bundle. MSCNN and
  TCN in that bundle are also disclosed train-split weights. BeatFM remains a
  stopped, reduced-data experiment and is not included.
- The final README submitted to MIREX will contain only the command lines that
  we actually want the organizers to execute; examples above are capability
  documentation, not a request to evaluate every Cartesian-product variant.

## Contact

Zhanh He — project contact via
[github.com/zhanh-he/casm-beat-tracking](https://github.com/zhanh-he/casm-beat-tracking).
