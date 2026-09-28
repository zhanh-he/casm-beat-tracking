# CASM beat tracking

CASM is a lightweight confidence-adaptive semi-Markov postprocessor for framewise beat and downbeat activations. The public API uses the frozen **7F calibration** by default and depends only on NumPy and SciPy at inference time—no PyTorch model and no `madmom` state lattice are required.

This repository contains the decoder, frozen calibration record, reproducible result tables, experiment entry points, paper figures, and an interactive listening demo.

## Install

Install directly from GitHub:

```bash
python -m pip install 'git+https://github.com/zhanh-he/casm-beat-tracking.git'
```

For local development:

```bash
python -m pip install -e .
```

Once the package is available on PyPI, installation will be:

```bash
python -m pip install casm-beat-tracking
```

The distribution name is `casm-beat-tracking`; the Python import is `casm_beat_tracking`.

## Madmom-style processor

The high-level interface follows madmom's callable processor convention and its `[time, beat_number]` output layout:

```python
import numpy as np
from casm_beat_tracking import CASMDownBeatTrackingProcessor

activations = np.load("activations.npy")  # (frames, 2), beat then downbeat
processor = CASMDownBeatTrackingProcessor(input_type="probabilities")
events = processor(activations)            # (num_beats, 2)
```

`CASMProcessor` is the short alias; `CASMBeatTrackingProcessor` returns beat times from one-dimensional activations. This is a familiar processor interface, not a complete drop-in replacement for madmom: CASM starts from framewise activations and intentionally does not bundle an audio frontend or neural model. See the [Python API contract](casm/docs/API.md) for details.

For separate logit arrays and separate beat/downbeat outputs, use the lower-level API:

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
# A two-column (beat, downbeat) activation matrix is also accepted:
casm-decode activations.npy --output track.beats
# For probabilities rather than logits:
casm-decode track.npz --input-type probabilities --output track.npz
```

The two inputs must be finite, one-dimensional, equal-length arrays sampled at 50 Hz. The default keys are `beat_logits` and `downbeat_logits`; `--beat-key` and `--downbeat-key` support other `.npz` layouts. Output may be compressed `.npz` (`beats`, `downbeats`) or tab-separated `.beats`/`.tsv`/`.txt`.

The interface follows the practical “activations in, event times out” pattern used by [madmom](https://github.com/CPJKU/madmom) and the local-periodicity emphasis of [PLPDP](https://github.com/SunnyCYC/plpdp4beat). CASM keeps inference small by running its dynamic program over activation peaks rather than a dense tempo/meter state lattice.

## Frozen 7F default

The default was selected on the union of SMC folds 1–7, with fold 0 excluded from decoder selection. It is global: CASM does not tune itself per track and has no learned weights or random seed.

- Human-readable protocol and complete parameter table: [calibration documentation](casm/docs/CALIBRATION.md)
- Machine-readable default: [7F JSON](casm/config/casm-7f-default.json)
- Candidate hash: `93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de`

Use `CASMConfig.from_json(...)` only when reproducing a named configuration; ordinary inference should use `CASMDecoder()`.

## Results

The locked Beat This-backbone evaluation contains 4,556 pieces across all eight backbone-held-out partitions:

| Scope | Beat F | Beat CMLt | Beat AMLt | Downbeat F | Downbeat CMLt | Downbeat AMLt |
|---|---:|---:|---:|---:|---:|---:|
| All pieces | 89.5 | 80.0 | 87.8 | 86.8 | 77.0 | 85.0 |
| SMC (217-piece macro) | 62.9 | 53.7 | 63.5 | — | — | — |
| SMC (8-fold mean ± SD) | 63.0 ± 3.3 | 53.8 ± 7.8 | 63.6 ± 5.9 | — | — | — |

The full per-dataset table, fold-level SMC table, GTZAN caveat, and Beat This/MSCNN-lite/TCN release matrix are in the [results documentation](experiments/tables/RESULTS.md). Run this local, cluster-free check to validate the locked source and rebuild all public tables:

```bash
python experiments/tables/build_results_tables.py
```

GTZAN mean ± standard deviation and the MSCNN-lite/TCN frozen-7F refreshes remain explicitly pending. Historical settings are not mixed into the final-7F table.

## Speed and dependencies

CASM has no audio frontend or neural-network dependency. On one Apple M4 run, the high-level processor decoded a synthetic 30-minute activation sequence in a median 0.192 seconds after warm-up (about 9,367× real time); the low-level decoder took 0.190 seconds. This is a point measurement, not a cross-library benchmark; reproduce it on your machine with:

```bash
python casm/benchmarks/benchmark_decoder.py --api processor --minutes 30 --repeats 5
```

## Reproduction and provenance

- [Data and annotations](experiments/DATA_AND_ANNOTATIONS.md): Beat This annotation version, splits, and exact spectrogram recipe.
- [Experiments](experiments/README.md): cached-activation evaluation contract and eight-fold command.
- [Checkpoint plan](casm/weights/README.md): publication and recovery status.
- [Checkpoint manifest](casm/weights/manifest.json): recoverable sizes and SHA-256 hashes.
- [Locked result source](experiments/tables/source/locked-7f/): compact source bundle used by the public table validator.

The experiments use [Beat This](https://github.com/CPJKU/beat_this) data organization, annotations, preprocessing, and backbone outputs. CASM does not redistribute audio.

## Demo and repository layout

The existing interactive comparison remains available at [zhanh-he.github.io/casm-beat-tracking](https://zhanh-he.github.io/casm-beat-tracking/).

- `casm/`: installable decoder, frozen defaults, weight manifest, tests, benchmarks, and API documentation.
- `experiments/`: decoder/backbone protocols, paper figures, validated tables, and compact result sources.
- `online-demo/`: interactive GitHub Pages site, audio excerpts, and
  visualization data.
- `archive/`: a public pointer for the authors' local research archive; the
  manuscript, reading, presentation, and historical figure workspaces are kept
  out of the release repository.
