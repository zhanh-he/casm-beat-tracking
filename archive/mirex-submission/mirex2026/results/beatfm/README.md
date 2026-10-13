# BeatFM: epoch 15 selected on allowed Ballroom/RWC validation

The 911-piece original-WAV Ballroom/RWC subset completed sliding-clip
training on Kaya (job `45647`; 774 train / 137 piece-disjoint validation;
22 epochs before early stop). Five predeclared epoch states were evaluated
on the **same 137 allowed-validation recordings** with Direct, frozen no-SMC
CASM, DBN 55–215 BPM, and exploratory DBN 30–300 BPM. All values below are
piece-macro percentages, **not official MIREX test scores**. SMC and GTZAN
were absent from training, validation, checkpoint choice, and this report.

## Checkpoint choice

The rule was fixed before reading scores: maximize Direct's
`0.50 × beat F + 0.25 × beat CMLt + 0.25 × beat AMLt` over the common 137-piece
panel. CASM/DBN rows were not used to choose a checkpoint. The choice is
**epoch 15**, not the epoch-2 minimum validation-loss checkpoint.

| Candidate | Epoch | Validation loss | Direct selection score | Beat F | CMLt | AMLt |
|---|---:|---:|---:|---:|---:|---:|
| Best loss | 2 | 0.8657 | 72.64 | 81.56 | 59.79 | 67.65 |
| Periodic | 5 | 0.8698 | 73.92 | 82.66 | 61.45 | 68.92 |
| Periodic | 10 | 0.9057 | 73.68 | 82.83 | 61.28 | 67.77 |
| **Selected** | **15** | 0.9769 | **73.99** | **82.89** | **62.00** | **68.18** |
| Periodic | 20 | 0.9935 | 73.85 | 82.89 | 62.00 | 67.60 |

The 0.07-point selection-score advantage over epoch 5 is small; it is a
deterministic allowed-validation choice, not evidence of a meaningful
generalization gap. Selected checkpoint SHA-256:
`44a1a33f6c3d08180bea2f0619c16a39a756644f101d0cd5d1691f7abd8ba764`.

## Same checkpoint, four decoders

| Decoder | Beat F | Beat CMLt | Beat AMLt | Downbeat F |
|---|---:|---:|---:|---:|
| Direct | 82.89 | 62.00 | 68.18 | 60.01 |
| CASM, frozen no-SMC 30–300 | **83.98** | 65.88 | 71.96 | 65.93 |
| DBN 55–215 | 82.54 | **70.38** | 82.02 | **77.55** |
| DBN 30–300, exploratory | 81.95 | 68.88 | **84.96** | 76.86 |

CASM improves beat F by 1.09 percentage points, CMLt by 3.88 points, and
AMLt by 3.78 points relative to Direct on this development panel. DBN trades
lower beat F for substantially higher AMLt and downbeat F. On the 34 RWC
recordings, CASM beat F is 75.50%, while default DBN is 65.36%; on the 103
Ballroom recordings, default DBN is 88.21% versus CASM's 86.78%. The
per-dataset F/CMLt/AMLt values for every decoder are in
[`allowed_eval_911_5090_20261004/summary.csv`](allowed_eval_911_5090_20261004/summary.csv).

The [frozen selection record](allowed_eval_911_5090_20261004/selection.json),
[piece rows](allowed_eval_911_5090_20261004/pieces.csv), and
[evaluation provenance](allowed_eval_911_5090_20261004/provenance.json)
allow the table to be rebuilt. Every candidate/decoder has 137 unique piece
rows. The original training split manifest SHA-256 is
`24deea630d5c7d8bf88f4f1d9c035c3370ae3a5ff181d448e5a164a9f5e13f1b`;
the private 137-WAV transfer archive was SHA-256-verified on 5090 as
`ac29d9582cd69a8c0c851fee4a999b018d04b2b6c32cb4812cafe44dc7ac4887`.
The CSV of all 2,740 piece/decoder/candidate rows has SHA-256
`f5dd7327cfde97fc06ef68bf45aafa6063a4ff00f2971ed30b6750eddd783ec1`.

This is a **reduced-data, train-split candidate**. It is not an equal-data
comparison to the 4,339-piece BeatThis pool or an exact reproduction of the
BeatFM paper. The separate 1,684-piece run (Kaya `69061`) completed after
25 epochs with early stopping. Its dependency-linked common-panel score job
`69066` failed before scoring due to a file-staging error; corrected retry
`70943` was cancelled on 2026-10-05 at the user's request to stop BeatFM
experiments. It ran for zero seconds. No BeatFM job remains queued on Kaya or
Gadi, and no BeatFM inference process was found on lab5090. Existing weights,
logs, and earlier validation results were retained. The 911-piece
checkpoint has not yet been retrained on all 911 allowed pieces. CASM was
calibrated using an allowed validation pool that includes these recordings,
so the decoder comparison is development evidence rather than an unbiased
generalization estimate. Source/MERT rights still need checking before an
external BeatFM bundle is distributed. See the
[source/data audit](../../backbone-retrain/BEATFM_SOURCE_AUDIT.md).

## Expanded-run early check (not a checkpoint choice)

While the 1,684-piece run was still training, its epoch-2 best-loss snapshot
was frozen and evaluated by inference only on the *same* 137 Ballroom/RWC
validation pieces. The expanded manifest, relocated audio/annotation IDs,
and snapshot SHA-256 were verified before scoring. This is a diagnostic of
the run's early trajectory, not a comparison of final trained systems and
not a reason to alter the predeclared five-candidate selection.

| Snapshot | Decoder | Beat F | CMLt | AMLt | Downbeat F |
|---|---|---:|---:|---:|---:|
| Expanded epoch 2 | Direct | 81.56 | 58.25 | 66.99 | 54.50 |
| Expanded epoch 2 | CASM | 82.40 | 61.26 | 70.88 | 58.52 |
| Expanded epoch 2 | DBN 55–215 | 79.67 | 65.59 | 85.83 | 69.37 |
| Expanded epoch 2 | DBN 30–300 | 79.03 | 62.87 | 86.47 | 67.39 |

The matching 911-piece selected epoch-15 Direct/CASM beat F values above
are 82.89/83.98, so the expanded run has **not yet** surpassed the current
private submission candidate. The expanded snapshot SHA-256 is
`560c0f4b3ed9e6860919beed700b77beac9fd58424bcf35b3f508955c41610b1`;
its [full early-check summary](expanded_interim_epoch2_common137_20261004/summary.csv)
and [provenance](expanded_interim_epoch2_common137_20261004/provenance.json)
are retained for audit. The final five-checkpoint evaluation is cancelled,
not pending.
