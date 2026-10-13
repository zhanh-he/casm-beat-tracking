# Frozen target-diagnostic table inputs — 2026-10-05

This directory preserves the exact inputs behind
[`../MODEL_DECODER_MATRIX_20261005.md`](../MODEL_DECODER_MATRIX_20261005.md).
It is a quarantined research diagnostic, not an official MIREX result and not
an eligible source for submission model or decoder selection.

The frozen 5090 manifest contains three checkpoints whose seed/epoch decisions
were made using allowed validation only:

- MSCNN seed 0, epoch 1499, trained on 3,783 pieces;
- TCN seed 0, zero-based epoch 119, trained on 3,783 pieces;
- TCN seed 0, 120-epoch full retrain on all 4,339 allowed pieces.

Every model produced exactly 993 GTZAN and 217 SMC caches. Each decoder's
`.pieces.csv` has 1,210 unique model/dataset pieces and reuses the same frozen
logit cache across Direct, CASM, DBN 55–215, and DBN 30–300. SMC has no
downbeat reference in this protocol. The two BeatThis CSVs were produced by
the earlier identical target-comparison protocol for the selected 3,783-piece
weight and the final 4,339-piece weight.

Source hashes:

| File | SHA-256 |
|---|---|
| `target_comparison_beatthis_split.csv` | `64758983f238b1a62da9292ef7e2fbb64b7cd1585557bbd8163e69c6c140f732` |
| `target_comparison_beatthis_full_and_baselines.csv` | `92fbd5106eba07d02ad81545f81ef2d55d6dceb8e7758736791babc47e44bfcf` |
| `target_comparison_mscnn_tcn.csv` | `f36c64aecb367d143d815df2c2e144203af4d58db2c495ae38e8f175a64a5b4a` |
| `models.frozen.tsv` | `fcd407a46bd94aeaa474b2f3a404aa949e0f1f1b2f364c4c500214a3ba46bba6` |

The MIREX 2026 beat task forbids using SMC or GTZAN for any development
purpose, and the downbeat task applies the same restriction to GTZAN. These
scores therefore cannot be used to choose a checkpoint, decoder, parameter,
or submitted system.
