# Released-default PLPDP diagnostic — 2026-10-07

These are **post-freeze diagnostics**, not official MIREX scores or evidence
for choosing the submitted weights or decoders. The three submitted split
weights (BeatThis seed 2/epoch 119, MSCNN seed 0/epoch 1499, TCN seed
0/epoch 119) were fixed using allowed validation before this panel. Two
separately labelled full-data research weights are also shown in the main
README table, but are not in the MIREX submission bundles.

The same frozen frame-logit caches and `mir_eval` metric protocol used for
Direct, CASM, and DBN were reused. Each of the five model panels contains
993 GTZAN and 217 SMC pieces. SMC has beat labels only. The decoder is the
released PLPDP default: beat activation is `max(sigmoid(beat),
sigmoid(downbeat))`; 50-fps values are linearly interpolated to the reference
implementation's 100 fps; BPM support is 30–300; downbeats come from Direct
downbeat peaks snapped onto PLPDP's selected beat grid. No PLPDP parameter
was tuned on GTZAN or SMC.

The reference implementation is
[SunnyCYC/plpdp4beat](https://github.com/SunnyCYC/plpdp4beat), commit
`30df4300849c843a7533e995113f4d26cd1e7d12` (MIT), with
`libfmp==1.3.0`. The five `raw/*_plpdp.pieces.csv` files contain the
individual measurements and the paired `summary.json` files contain macro
averages. `../../scripts/build_decoder_delta_table.py` checks SHA-256,
dataset counts, unique piece IDs, and each displayed aggregate against the
piece-level rows before regenerating the main table.

The paper's controlled ICASSP eight-fold experiment and this MIREX protocol
use different backbone weights and training exclusions. The PLPDP comparison
is therefore mixed here: CASM should not be described as outperforming
PLPDP on **every** metric in this diagnostic panel. In particular, PLPDP has
a slightly higher GTZAN beat F1 for submitted BeatThis and MSCNN, while CASM
has larger GTZAN downbeat continuity gains on those same weights. Report
the relevant task and metric, and do not use this panel for MIREX model or
decoder selection.
