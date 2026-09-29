# BeatThis no-SMC seed-0, 100-epoch diagnostic

This is a diagnostic readout, not a checkpoint-selection table. The underlying
[12-row result table](beatthis_seed0_e100_disjoint.csv) was rebuilt from cached
logits after excluding every model/dataset pair with training overlap. The
official BeatThis `final0` model appears on GTZAN only; it trained on SMC and
has no SMC result in this artifact. The corrected remote artifact is:

The CASM rows below used the **MIREX-specific no-SMC configuration** in
[`../config/casm-no-smc.json`](../config/casm-no-smc.json), calibrated on 556
allowed-validation pieces; they did not use the released 7F default. Neither
SMC nor GTZAN was used for this backbone's training/selection or this
decoder's calibration. These panels remain post-freeze diagnostics, not
checkpoint-selection data or official MIREX scores.

`/storage/zhanh_storage/auto_structbeat_runs/beatthis_final_nosmc_seed0_e100_20260929T1145/evaluation_disjoint_baseline_rebuild_20260929`

The earlier 16-row artifact and its official-final0 SMC cache were deleted.
The remote corrected CSV SHA-256 is
`366fccb3f191e43f0375c2fdad8f8bae1e4605c82cc45fadbaa0dfc17724e5eb`.
The identical rows in this repository use LF line endings and have SHA-256
`9da8cb66365816976fc7a066f8dd20b39bae869b3aa5a7a29de280d8f96b8d6d`.

## No-SMC model, same 217 SMC pieces

| Decoder | Beat F | Beat CMLt | Beat AMLt |
|---|---:|---:|---:|
| Direct | 58.86% | 43.34% | 53.97% |
| CASM | 58.94% | 44.49% | 55.92% |
| DBN 55–215 | 55.96% | 42.48% | 59.50% |
| DBN 30–300 | 56.07% | 44.14% | 60.19% |

Compared with Direct on identical activations, CASM changes beat F by only
+0.08 percentage points (paired piece bootstrap 95% interval −0.21 to +0.38).
It raises CMLt by +1.15 points (interval +0.46 to +1.88) and AMLt by +1.95
points (interval +1.25 to +2.67). Under the no-SMC training and calibration
protocol, this is evidence of a continuity gain on this unseen SMC panel,
not a beat-F improvement claim.

The paper's BeatThis eight-fold out-of-fold Direct result is 62.70% on SMC.
Those fold models trained on other SMC folds, so it is contextual information,
not a matched no-SMC baseline.

## No-SMC model, same 993 GTZAN pieces

| Decoder | Beat F | Beat CMLt | Downbeat F | Downbeat CMLt |
|---|---:|---:|---:|---:|
| Direct | 89.58% | 80.68% | 78.20% | 67.36% |
| CASM | 89.62% | 81.05% | 77.92% | 71.57% |
| DBN 55–215 | 88.57% | 81.04% | 77.23% | 73.19% |
| DBN 30–300 | 89.01% | 81.21% | 77.74% | 73.71% |

CASM versus Direct: beat F +0.04 points (interval −0.03 to +0.11), beat CMLt
+0.37 (+0.22 to +0.54), downbeat F −0.28 (−0.98 to +0.41), and downbeat
CMLt +4.21 (+2.72 to +5.75). Again the measured gain is continuity, while
F-measure is essentially unchanged. DBN has still higher downbeat continuity
on this panel, with lower beat F; this tradeoff needs clean allowed-validation
assessment before a submission choice.

On GTZAN alone, official `final0` Direct gives 89.22% beat F and 78.71%
downbeat F. Our no-SMC Direct model gives 89.58% and 78.20%. Paired
differences are +0.37 beat-F points (interval −0.08 to +0.84) and −0.51
downbeat-F points (interval −1.42 to +0.41). The intervals include zero, so
this baseline does not establish a reliable advantage over official `final0`.

The paired intervals use 10,000 piece-level bootstrap resamples with seed
20260929. SMC and GTZAN were excluded from backbone training, checkpoint
selection, and the no-SMC CASM decoder calibration. These panels remain
diagnostics only. The final
BeatThis seed, epoch, and decoder choice must come from the allowed validation
set.
