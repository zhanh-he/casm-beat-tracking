# Backbone × training pool × decoder matrix (2026-10-05)

This table records **beat** F1/CMLt/AMLt as piece-macro percentages. A slash
separates the two decoders named in the same row. Bold marks the maximum among
the four decoders only where all four results actually exist. `—` means there
is no verified score; it is never a zero or an estimate. This is a status
matrix, **not** a set of official MIREX test results or a submission selector.

| Model weight | Training data (pieces) | Postprocessing | GTZAN F1, CMLt, AMLt | SMC F1, CMLt, AMLt |
|---|---|---|---|---|
| BeatThis seed-0 e100, **historical diagnostic only** | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | 89.58, 80.68, 90.68 / **89.62**, 81.05, 91.16 | 58.86, 43.34, 53.97 / **58.94**, **44.49**, 55.92 |
|  |  | DBN 55–215 / DBN 30–300 | 88.57, 81.04, 91.42 / 89.01, **81.21**, **92.56** | 55.96, 42.48, 59.50 / 56.07, 44.14, **60.19** |
| BeatThis seed-2 e119, selected on allowed validation | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| BeatThis seed-2 e120, full retrain | 4,339; same log-Mel; no held-out validation during final retrain | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| MSCNN seed-0 e1499 | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| MSCNN, **not trained** | 4,339; same log-Mel; full-retrain plan only | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| TCN seed-0 e119 / best-loss candidate, selection running | 3,783; BeatThis log-Mel; 556 allowed validation | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| TCN, **not trained** | 4,339; same log-Mel; full-retrain plan only | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| BeatFM e15, experiments stopped | 911 mapped WAV pool: **774 train + 137 validation**, not full-911 training | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| BeatFM expanded, experiments stopped | 1,684 mapped WAV pool: **1,431 train + 253 validation**, not 1,431 full-pool or 1,684 full training | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| SpecTNT, **not implemented** | 3,783 planned; input/architecture adaptation unverified | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |
| SpecTNT, **not implemented** | 4,339 planned; input/architecture adaptation unverified | Direct / CASM | — / — | — / — |
|  |  | DBN 55–215 / DBN 30–300 | — / — | — / — |

The only numeric target-set row above is the previously generated no-SMC
BeatThis seed-0/100-epoch diagnostic in
[`beatthis_seed0_e100_disjoint.csv`](beatthis_seed0_e100_disjoint.csv): 993
GTZAN and 217 SMC pieces. It is **not** the selected seed-2 checkpoint.
Upstream BeatThis `final0` is excluded entirely from SMC because its training
included SMC folds. Selected BeatThis, MSCNN, and BeatFM have allowed-validation
decoder panels in their respective result directories; these are not
interchangeable with the GTZAN/SMC columns above.

The MIREX 2026 task page forbids using **any split of SMC or GTZAN** for
training, validation, model selection, parameter tuning, or other development.
Therefore neither the historical diagnostic row nor any future organizer test
scores can select MIREX checkpoints/decoders. TCN's old paused screen job
`39247`, which would have promoted SMC/GTZAN diagnostic roles, was cancelled.
The replacement Kaya job `71534` reads only 556 allowed validation pieces,
freezes one checkpoint, and compares the four decoders on that pool. Its
dependent Kaya job `71653` then retrains the same seed for the chosen number
of epochs on all 4,339 allowed pieces using `--no-val`; any validation metric
printed during that final run overlaps training and is ineligible as an
independent score. BeatFM retry `70943` was cancelled before running;
existing BeatFM artifacts remain.
