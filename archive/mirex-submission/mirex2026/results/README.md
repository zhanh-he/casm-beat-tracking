# MIREX allowed-validation results and quarantined historical diagnostics

Current development evidence is the
[BeatThis seed-2 allowed-validation decoder panel](beatthis_seed2_allowed_panel_20261004/README.md)
and the [MSCNN four-checkpoint allowed-validation screen](mscnn_seed0_allowed_screen_20261004/README.md).
The [TCN nine-state allowed-validation screen](tcn_seed0_allowed_20261005/README.md)
has now selected its seed-0 epoch-119 state; full-allowed-data retraining is
queued separately.
The [BeatFM five-checkpoint score](beatfm/README.md) selects epoch 15 on
137 allowed Ballroom/RWC recordings. An [exact matched-piece matrix](common_allowed_137_20261004/README.md)
reports all three backbones × four decoders on those same 137 IDs. None is an
official MIREX test score. The primary BeatThis full-allowed-data retrain has
separate weights; its former validation pieces are no longer held out.
The [requested GTZAN/SMC matrix](MODEL_DECODER_MATRIX_20261005.md) shows
verified historical values and explicit missing-result cells for BeatThis,
MSCNN, TCN, BeatFM, and SpecTNT; it must not be used for MIREX development.
The former main-README [nine-metric absolute table](absolute-score-table/README.md)
is preserved verbatim; the main README now shows Direct absolute scores and
CASM/DBN/PLPDP percentage-point differences relative to Direct. The
[released-default PLPDP panel](plpdp_default_20261007/README.md) retains
all 6,050 piece-level rows and the five aggregate summaries used to extend
that table; it is a post-freeze target diagnostic, not MIREX selection evidence.

The [MIREX 2026 task rule](https://music-ir.org/mirex/wiki/2026:Audio_Beat_Tracking)
prohibits SMC and GTZAN for **any development purpose**, including model
selection and tuning. Never use the older target-set files below to make a
competition decision.

The [BeatThis seed-0 diagnostic](BASELINE_DIAGNOSTIC.md) and its
[12-row CSV](beatthis_seed0_e100_disjoint.csv) use only checkpoint/dataset
pairs approved by the provenance gate. Official BeatThis `final0` is shown
on GTZAN only, never on SMC, because its training included SMC.

The [2026-09-29 experiment recovery](RECOVERY_2026-09-29.md) adds the completed
BeatThis single-split checkpoint screen, the expanded-search status, and the
MSCNN seed-0 training/screening status. Its subfolders preserve small raw
result manifests with source SHA-256 hashes. These are not final competition
results.

The 911-piece Ballroom/RWC BeatFM candidate finished training on Kaya job
`45647` and was scored on lab5090 (inference only). Kaya launchers `69059`
and `69065` failed before scoring; queued duplicate `69069` was cancelled
after the 5090 result was validated. An expanded 1,684-piece audio-matched
training run completed as job `69061` (25 epochs). Its dependency evaluation
job `69066` failed before scoring due to a staging-path error; corrected
retry `70943` was cancelled before running on 2026-10-05 at the user's
request to stop all BeatFM experiments. This is not an
equal-data BeatThis reproduction. Full-pool
BeatFM training still lacks the remaining original audio. The one-epoch
engineering pilot is not a scoring checkpoint.

The allowed-validation panels above are the documented basis for their stated
seed/epoch choices, but are not official MIREX test scores. The quarantined
historical target-set diagnostics are **never** used for MIREX model choices.
Final system identifiers and official organizer results remain pending. Keep
future result files here with the
checkpoint hash, data/split inventory, decoder configuration hash, and
evaluation eligibility stated explicitly.
