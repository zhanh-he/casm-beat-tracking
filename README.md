# CASM beat tracking

CASM is a lightweight confidence-adaptive semi-Markov postprocessor for framewise beat and downbeat activations. The release API uses the frozen **7F calibration** by default and depends only on NumPy and SciPy at inference time—no PyTorch model and no `madmom` state lattice are required.

This branch is a paper-revision release candidate. The CASM decoder, calibration record, reproducible result tables, checkpoint inventory, and experiment entry points are organized here for review before anything is merged to `main`.

## Install and decode

```bash
python -m pip install -e .
```

From Python:

```python
import numpy as np
from casm_beat_tracking import CASMDecoder

activations = np.load("track.npz")
beats, downbeats = CASMDecoder().decode(
    activations["beat_logits"],
    activations["downbeat_logits"],
)
```

Or from the command line:

```bash
casm-decode track.npz --output track.beats
# For probabilities rather than logits:
casm-decode track.npz --input-type probabilities --output track.npz
```

The two inputs must be finite, one-dimensional, equal-length arrays sampled at 50 Hz. The default keys are `beat_logits` and `downbeat_logits`; `--beat-key` and `--downbeat-key` support other `.npz` layouts. Output may be compressed `.npz` (`beats`, `downbeats`) or tab-separated `.beats`/`.tsv`/`.txt`.

The interface follows the practical “activations in, event times out” pattern used by [madmom](https://github.com/CPJKU/madmom) and the local-periodicity emphasis of [PLPDP](https://github.com/SunnyCYC/plpdp4beat). CASM keeps inference small by running its dynamic program over activation peaks rather than a dense tempo/meter state lattice.

## Frozen 7F default

The default was selected on the union of SMC folds 1–7, with fold 0 excluded from decoder selection. It is global: CASM does not tune itself per track and has no learned weights or random seed.

- Human-readable protocol and complete parameter table: [`docs/CALIBRATION.md`](docs/CALIBRATION.md)
- Machine-readable default: [`config/casm-7f-default.json`](config/casm-7f-default.json)
- Candidate hash: `93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de`

Use `CASMConfig.from_json(...)` only when reproducing a named configuration; ordinary inference should use `CASMDecoder()`.

## Results

The locked Beat This-backbone evaluation contains 4,556 pieces across all eight backbone-held-out partitions:

| Scope | Beat F | Beat CMLt | Beat AMLt | Downbeat F | Downbeat CMLt | Downbeat AMLt |
|---|---:|---:|---:|---:|---:|---:|
| All pieces | 89.5 | 80.0 | 87.8 | 86.8 | 77.0 | 85.0 |
| SMC (217-piece macro) | 62.9 | 53.7 | 63.5 | — | — | — |
| SMC (8-fold mean ± SD) | 63.0 ± 3.3 | 53.8 ± 7.8 | 63.6 ± 5.9 | — | — | — |

The full per-dataset table, fold-level SMC table, GTZAN caveat, and Beat This/MSCNN-lite/TCN release matrix are in [`docs/RESULTS.md`](docs/RESULTS.md). Run this local, cluster-free check to validate the source and rebuild all public tables:

```bash
python scripts/build_results_tables.py
```

GTZAN mean ± standard deviation and the MSCNN-lite/TCN frozen-7F refreshes remain explicitly pending. Historical settings are not mixed into the final-7F table.

## Speed and dependencies

CASM has no audio frontend or neural-network dependency. On one Apple M4 run, the included synthetic 30-minute activation benchmark decoded in a median 0.192 seconds after warm-up (about 9,400× real time). This is a point measurement, not a cross-library benchmark; reproduce it on your machine with:

```bash
python benchmarks/benchmark_decoder.py --minutes 30 --repeats 5
```

## Reproduction and provenance

- [`docs/DATA_AND_ANNOTATIONS.md`](docs/DATA_AND_ANNOTATIONS.md): Beat This annotation version, splits, and exact spectrogram recipe.
- [`experiments/README.md`](experiments/README.md): cached-activation evaluation contract and eight-fold command.
- [`weights/README.md`](weights/README.md): checkpoint publication plan and recovery status.
- [`weights/manifest.json`](weights/manifest.json): recoverable checkpoint sizes and SHA-256 hashes.
- [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md): remaining publication blockers.

The experiments use [Beat This](https://github.com/CPJKU/beat_this) data organization, annotations, preprocessing, and backbone outputs. CASM does not redistribute audio.

## Demo and repository layout

The existing interactive comparison remains available at [zhanh-he.github.io/casm-beat-tracking](https://zhanh-he.github.io/casm-beat-tracking/).

- `src/casm_beat_tracking/`: installable decoder and CLI.
- `config/`: frozen defaults.
- `tests/` and `benchmarks/`: local correctness and throughput checks.
- `experiments/`: readable evaluation entry points.
- `results/` and `docs/`: validated tables, methods, provenance, and demo.
- `Paper/` and `self-run-figures/`: existing paper/reproduction workspaces.

Public release still requires an explicit license choice for this code and the CASM-trained weights.
