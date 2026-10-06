# Archived absolute-score MIREX diagnostic table

This is the former nine-metric table from `mirex2026/README.md`, preserved with its original absolute values and missing cells. It is a historical post-freeze diagnostic, not an official MIREX result or permitted model-selection evidence. The current main README presents decoder differences relative to Direct.

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
| MSCNN seed-0 e1500, full retrain incomplete | 4,339 log-Mel; no held-out validation | Direct / CASM | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |
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

Source CSVs and hashes: [`target_table_20261005/`](../target_table_20261005/). GTZAN and SMC diagnostics must not be used for any MIREX development decision.
