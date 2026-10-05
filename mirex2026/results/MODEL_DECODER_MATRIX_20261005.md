# Backbone × training pool × decoder matrix (2026-10-05)

Values are piece-macro percentages. A slash separates the two decoders named
in the same row. Bold marks the maximum among the four decoders for one fixed
model weight and metric. `—` means no verified result, never zero. GTZAN uses
993 valid pieces and has beat and downbeat annotations; SMC uses 217 pieces
and has beat annotations only.

| Model weight | Training data (pieces) | Postprocessing | GTZAN beat (F1, CMLt, AMLt) | GTZAN downbeat (F1, CMLt, AMLt) | SMC beat (F1, CMLt, AMLt) |
|---|---|---|---|---|---|
| BeatThis seed-2 e119 | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | 88.96, 79.64, 89.66 / **89.00**, 79.86, 90.07 | **78.05**, 66.52, 79.79 / 77.75, 70.98, 84.86 | 57.75, 41.74, 52.30 / **57.99**, 43.34, 54.68 |
|  |  | DBN 55–215 / DBN 30–300 | 88.36, **80.98**, 91.61 / 88.50, 80.49, **92.23** | 76.99, 72.55, 88.20 / 77.39, **72.61**, **88.56** | 54.59, 42.27, 58.25 / 54.66, **43.38**, **58.43** |
| BeatThis seed-2 e120, full retrain | 4,339; same log-Mel; no held-out validation | Direct / CASM | 88.78, 79.04, 89.61 / 88.83, 79.30, 90.11 | 77.76, 66.95, 80.31 / 77.74, 71.52, 84.40 | **59.21**, 43.73, 55.50 / 58.97, 44.41, 57.11 |
|  |  | DBN 55–215 / DBN 30–300 | 88.33, 80.59, 91.48 / **88.94**, **80.71**, **92.51** | 77.12, 72.77, 87.60 / **77.84**, **73.31**, **88.12** | 56.31, 43.90, **61.22** / 56.53, **44.96**, 60.51 |
| MSCNN seed-0 e1499 | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | 85.94, 72.18, 78.95 / **86.30**, 73.33, 80.42 | 69.59, 50.77, 61.63 / 71.66, 61.17, 72.43 | 54.81, 34.81, 41.57 / **55.72**, **39.27**, 46.94 |
|  |  | DBN 55–215 / DBN 30–300 | 85.52, **76.90**, **86.74** / 84.54, 74.80, 85.88 | **72.09**, **68.78**, **84.92** / 71.25, 67.25, 84.31 | 50.46, 39.11, **53.45** / 46.91, 32.89, 49.79 |
| MSCNN, not trained | 4,339; same log-Mel; full-retrain slot | Direct / CASM | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — |
| TCN seed-0 e119 | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | 86.54, 72.81, 80.54 / **86.81**, **73.82**, 81.76 | 61.23, 21.29, 59.29 / 65.92, 51.74, 70.96 | 51.54, 27.76, 33.43 / **51.85**, **30.06**, 37.93 |
|  |  | DBN 55–215 / DBN 30–300 | 84.52, 73.23, **86.54** / 83.87, 71.67, 86.32 | **66.58**, **59.77**, 82.16 / 65.87, 58.95, **82.41** | 42.09, 22.19, **39.71** / 36.72, 15.81, 36.70 |
| TCN seed-0 e120, full retrain | 4,339; same log-Mel; no held-out validation | Direct / CASM | 86.66, 73.20, 80.85 / **86.99**, **74.31**, 82.19 | 62.05, 24.25, 59.89 / **67.32**, 53.98, 71.41 | 51.41, 27.94, 33.81 / **51.78**, **30.24**, 37.93 |
|  |  | DBN 55–215 / DBN 30–300 | 84.11, 72.49, 86.16 / 83.78, 71.43, **86.41** | 67.24, **60.32**, **81.96** / 66.49, 58.97, 81.67 | 41.25, 21.16, 37.64 / 37.59, 15.51, **38.05** |
| BeatFM e15, experiments stopped | 911 mapped-WAV pool: 774 train + 137 validation | Direct / CASM | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — |
| BeatFM expanded, experiments stopped | 1,684 mapped-WAV pool: 1,431 train + 253 validation | Direct / CASM | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — |
| SpecTNT, placeholder | 3,783 planned; implementation and input adapter pending | Direct / CASM | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — |
| SpecTNT, placeholder | 4,339 planned; full-retrain slot | Direct / CASM | — / — | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — | — / — |

The BeatThis 3,783-piece weight was selected on allowed validation before its
target-set diagnostic. The 4,339-piece BeatThis and TCN weights were retrained
for the frozen duration on the complete allowed pool. TCN split selection used
only allowed validation; the final checkpoint SHA-256 is
`3fb04add5b37ea0f624ce63b60cb6e5e90725892363015e7d8f4f284e3833e98`.
The exact source CSVs and 5090 per-piece results are retained in
[`target_table_20261005/`](target_table_20261005/).

These local diagnostics are not official MIREX results and must not be used
to choose a submission. The MIREX 2026 task pages prohibit using GTZAN or SMC
for training, validation, model selection, parameter tuning, or any other
development purpose. Upstream BeatThis `final0` remains excluded from the SMC
table because it trained on SMC folds.
