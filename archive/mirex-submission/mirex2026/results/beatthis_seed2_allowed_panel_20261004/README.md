# BeatThis seed-2 allowed-validation decoder panel — 2026-10-04

This is the **search checkpoint** selected from the no-SMC, GTZAN-held-out
three-seed/200-epoch run, not the later full-allowed-data retrain checkpoint.
The 556-piece allowed-validation panel and every decoder consume the same
cached activations. SMC and GTZAN are absent from these result files and were
not used for this choice. All values are piece-macro percentages.

| Decoder | Beat F | Beat CMLt | Beat AMLt |
|---|---:|---:|---:|
| Direct | 92.74 | 85.45 | 88.74 |
| CASM, frozen no-SMC 30–300 | 92.88 | 86.04 | 89.43 |
| DBN 55–215 | 91.23 | 84.21 | 90.82 |
| DBN 30–300 (exploratory) | 91.99 | 85.99 | 91.17 |

The selection file records seed 2, zero-based epoch 119, candidate
`epoch_0119_2f56b23a`, source checkpoint SHA-256
`cd8a8c93b11c189daab497076261730bc8a059fa2b8d2b9c07b012c2d9c4bd4d`,
and an allowed Beatles Direct score of 90.94 under the frozen 60% beat/40%
downbeat F/CMLt/AMLt formula. The selected seed was then trained for 120
epochs on **all allowed development pieces**. That separate submission
checkpoint has SHA-256
`0fed3858ac75ec716e622c0a5bd50ee1345fb1443902d3024ecff5e88fa20053`.
Because its retraining includes the former validation pieces, the table above
is not an independent score of that final checkpoint.

The CASM configuration was calibrated on the same allowed-validation pool
using a different seed-0 search checkpoint. Therefore this table is a decoder
development comparison, not an independent generalization estimate or a MIREX
test score. Each `.pieces.csv` has 556 rows; source `.summary.json` files and
the frozen choice/transfer records are retained beside this README.
