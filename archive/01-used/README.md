# Figures currently selected for the paper

These are byte-for-byte copies of the current selected outputs in
[`../../experiments/figures/`](../../experiments/figures/). Keeping copies here
makes the figure archive self-contained without changing the canonical paper
paths.

| Figure | Archived output | Canonical output |
|---|---|---|
| Figure 2b, corrected | [PNG](figures/fig02b-correct.png) | [`experiments/figures/fig02b-correct.png`](../../experiments/figures/fig02b-correct.png) |
| Figure 2b, superseded | [PNG](figures/fig02b-wrong.png) | [`experiments/figures/fig02b-wrong.png`](../../experiments/figures/fig02b-wrong.png) |
| Figure 5, CASM | [PNG](figures/fig05_calibration_scale.png) | [`experiments/figures/fig05_calibration_scale.png`](../../experiments/figures/fig05_calibration_scale.png) |
| Figure 5b, DBN | [PDF](figures/fig05b_dbn_calibration_scale.pdf) | [`experiments/figures/fig05b_dbn_calibration_scale.pdf`](../../experiments/figures/fig05b_dbn_calibration_scale.pdf) |

The [`source/`](source/) directory holds the historical mechanism/gallery
plotting scripts, the 7F Figure 2 candidate-search traces and receipts, and
the small CASM/DBN calibration tables. The current DBN calibration driver is
also copied there. These are source snapshots, not a claim that every old
upstream training or cache dependency is bundled. For current numerical
evidence, use the validated files under `experiments/`, not historical
results embedded in a plotting script.

The original Figure 2b is retained with the explicit `-wrong` suffix for
auditability. It used a joint beat/downbeat DBN on SMC, although SMC supplies
beat-only ground truth. The corrected panel replays a beat-only DBN over the
same frozen Beat This activation. Direct, CASM, and PLPDP arrays are unchanged.
The complete correction receipt,
data, plotting code, and online-demo builder are in
[`source/self-run-figures/figures-20260904-1443/fig02b-correction/`](source/self-run-figures/figures-20260904-1443/fig02b-correction/).
