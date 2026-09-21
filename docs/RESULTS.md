# Results

## Beat This backbone: locked 7F eight-fold evaluation

These are piece-macro results for the selected 7F CASM calibration on all eight backbone-held-out partitions. Folds 1–7 informed decoder selection and fold 0 did not, so this is out-of-fold with respect to backbone training but not a nested estimate of decoder calibration. Metrics are shown as percentages. Downbeat metrics are unavailable for Simac and SMC because their Beat This annotation files do not contain beat-position labels.

| Dataset | Beat N | Beat F | Beat CMLt | Beat AMLt | Downbeat N | Downbeat F | Downbeat CMLt | Downbeat AMLt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ASAP | 473 | 77.2 | 53.1 | 61.0 | 473 | 61.7 | 28.3 | 52.3 |
| Ballroom | 685 | 97.4 | 96.4 | 97.1 | 685 | 95.7 | 94.7 | 96.1 |
| Beatles | 179 | 94.6 | 87.5 | 93.1 | 179 | 89.8 | 77.2 | 87.2 |
| Candombe | 35 | 99.7 | 99.8 | 99.8 | 35 | 99.8 | 99.9 | 99.9 |
| Filosax | 48 | 99.5 | 98.8 | 98.8 | 48 | 99.1 | 97.8 | 97.8 |
| Groove MIDI | 336 | 93.7 | 87.8 | 92.1 | 336 | 83.0 | 76.3 | 86.7 |
| GuitarSet | 180 | 92.1 | 83.1 | 91.2 | 180 | 88.4 | 81.7 | 90.1 |
| Hainsworth | 222 | 92.0 | 84.8 | 92.0 | 222 | 81.5 | 69.9 | 83.1 |
| Harmonix | 911 | 96.0 | 90.6 | 94.6 | 911 | 91.5 | 84.2 | 89.7 |
| HJDB | 235 | 98.2 | 97.4 | 98.1 | 235 | 96.4 | 95.6 | 96.7 |
| JAAH | 113 | 95.0 | 88.5 | 90.6 | 113 | 87.6 | 78.5 | 81.9 |
| RWC Classical | 61 | 77.2 | 53.7 | 62.7 | 61 | 68.4 | 43.3 | 57.9 |
| RWC Jazz | 50 | 83.5 | 73.7 | 76.1 | 50 | 81.4 | 74.5 | 79.2 |
| RWC Popular | 100 | 96.2 | 90.5 | 94.5 | 100 | 94.5 | 89.7 | 92.4 |
| RWC Royalty-Free | 15 | 94.3 | 86.7 | 93.3 | 15 | 94.1 | 87.2 | 87.2 |
| Simac | 595 | 78.0 | 56.4 | 86.0 | — | — | — | — |
| SMC | 217 | 62.9 | 53.7 | 63.5 | — | — | — | — |
| TapCorrect | 101 | 93.3 | 83.2 | 90.4 | 101 | 88.3 | 74.1 | 82.8 |
| **RWC (all)** | 226 | 88.1 | 76.6 | 81.8 | 226 | 84.5 | 73.6 | 79.8 |
| **All pieces** | 4556 | 89.5 | 80.0 | 87.8 | 3744 | 86.8 | 77.0 | 85.0 |

The source is the locked 4,556-piece evaluation for candidate `93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de`. The machine-readable table is [`../results/beat_this_8fold_7f_by_dataset.csv`](../results/beat_this_8fold_7f_by_dataset.csv), and [`../scripts/build_results_tables.py`](../scripts/build_results_tables.py) validates and rebuilds both files.

## SMC fold variation

| Fold | N | Beat F | Beat CMLt | Beat AMLt |
|---:|---:|---:|---:|---:|
| 0 | 27 | 65.8 | 62.9 | 75.9 |
| 1 | 27 | 63.5 | 49.7 | 62.8 |
| 2 | 27 | 60.3 | 54.6 | 64.7 |
| 3 | 27 | 62.9 | 56.3 | 60.9 |
| 4 | 27 | 65.6 | 58.6 | 61.9 |
| 5 | 27 | 61.9 | 49.8 | 57.0 |
| 6 | 27 | 66.8 | 60.3 | 66.7 |
| 7 | 28 | 56.9 | 38.3 | 58.6 |
| **Mean ± SD** | — | **63.0 ± 3.3** | **53.8 ± 7.8** | **63.6 ± 5.9** |

“Mean ± SD” is the unweighted mean and sample standard deviation across the eight held-out **fold-level piece macros**. It describes cross-fold variation, not repeated-training uncertainty. The 217-piece macro (which weights pieces equally rather than folds equally) is Beat F 62.9, CMLt 53.7, and AMLt 63.5.

## GTZAN status

The currently preserved 7F `final1` evaluation is a single post-hoc-selected point: Beat F 89.5, CMLt 81.1, AMLt 90.6; Downbeat F 79.1, CMLt 71.5, AMLt 85.3. It is **not** reported as mean ± standard deviation because it is one checkpoint selected using GTZAN Beat F and therefore is not a clean independent test estimate.

A publishable GTZAN mean ± standard deviation requires the frozen 7F decoder to be rerun on `final0`, `final1`, and `final2` without selecting on GTZAN. That refresh is intentionally pending while Kaya is under maintenance; no historical non-7F results have been relabelled as final 7F results.

## Backbone release matrix

| Backbone | Eight-fold 7F results | GTZAN mean ± SD | Checkpoints |
|---|---|---|---|
| Beat This | Validated above | Pending three-seed refresh | `final0`–`final2` and fold0–fold7 protected |
| MSCNN-lite | Pending cache recreation; the eight-fold activation cache was purged | Pending three-seed refresh | Three selected checkpoints protected |
| TCN | Pending frozen-7F refresh | Pending recovery/retraining | `final0` and `final1` recovered; `final2` and fold0–fold7 missing |

This table separates verified results from recovery work. See [`../weights/README.md`](../weights/README.md) for the checksum inventory and [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) for release blockers.

## Evaluation definitions

The evaluator removes the first five seconds and reports `mir_eval` beat F-measure (±70 ms), CMLt, and AMLt. “All pieces” is a macro average over pieces, not a dataset-balanced average. The calibration procedure and its non-nested-selection limitation are documented in [`CALIBRATION.md`](CALIBRATION.md).
