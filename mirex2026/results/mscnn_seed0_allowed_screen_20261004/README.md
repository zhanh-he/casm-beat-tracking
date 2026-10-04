# MSCNN seed-0 allowed-validation screen — 2026-10-04

Four predeclared, distinct epoch states from the single Kaya training run
(job `39249`) were evaluated on the identical 556-piece allowed-validation
pool. SMC and GTZAN are not in the pool and were not used for checkpoint
selection, tuning, or this decoder comparison. Numbers are piece-macro
percentages; the Beatles selection score weights beat 60% and downbeat 40%,
with each target 50% F, 25% CMLt, and 25% AMLt, using Direct only.

| Candidate | Epoch | Beatles selection score | All-allowed Direct beat F |
|---|---:|---:|---:|
| Best validation loss 0.6027 | 119 | 79.58 | 87.99 |
| Best validation loss 0.6081 | 139 | 80.19 | 87.85 |
| Best validation loss 0.6068 | 154 | 80.67 | 88.19 |
| **Last** | **1499** | **82.51** | **89.30** |

The last checkpoint is the clean choice under that rule; its SHA-256 is
`6cb647407caf367e1e3e66d13061a4459899f26e1ae0001e5c519cac95ab30b1`.
It is a **train-split checkpoint**: unlike the primary BeatThis, no
all-allowed-data MSCNN retrain has been run. Its one-WAV Direct adapter smoke
test passed on an allowed Ballroom recording.

| Decoder on selected checkpoint | Beat F | Beat CMLt | Beat AMLt |
|---|---:|---:|---:|
| Direct | 89.30 | 78.29 | 80.75 |
| CASM, frozen no-SMC 30–300 | 89.80 | 79.86 | 82.51 |
| DBN 55–215 | 88.15 | 80.19 | 86.17 |
| DBN 30–300 (exploratory) | 87.88 | 80.25 | 85.81 |

`selection.json` stores the audited result rows and rule. The selector
recomputed metrics from each `.pieces.csv`, reconciled them to every source
summary, checked 556 unique piece/dataset keys for all 16 combinations, and
rejected SMC/GTZAN. The frozen CASM configuration was calibrated on this same
allowed pool via BeatThis, so this decoder table is development evidence, not
an independent generalization or official MIREX test score.
