# Why MIREX backbones are retrained

The ICASSP paper's BeatThis evaluation uses eight fold-specific backbone
checkpoints. Each SMC piece is predicted by a checkpoint that held out its
fold; the rest of SMC may still be present in that checkpoint's training.
That is appropriate for the paper's cross-validation protocol, but not for
an SMC-unseen MIREX diagnostic or a single deployable competition model.
The upstream BeatThis `final0` checkpoint also trained on SMC, so its full-SMC
score is training-set leakage, not a valid benchmark.

For MIREX, we therefore retrain the upstream BeatThis architecture and
training recipe with SMC and GTZAN excluded from backbone development. We
select seed, epoch, and decoder using only allowed validation pieces. After
freezing those decisions, the intended final model is retrained on the full
allowed pool, still excluding SMC and GTZAN. This is a different checkpoint
and data protocol, not a repeat of the ICASSP paper submission. CASM's
MIREX-specific no-SMC calibration is in `../config/casm-no-smc.json`; the
standalone public 7F decoder is a separate paper/release configuration.

## What is present

- [`train_beatthis_final_nosmc.sh`](train_beatthis_final_nosmc.sh) records the
  upstream-derived seed-0, 100-epoch no-SMC baseline command, including
  provenance hashes and milestone checkpoints. It expects a prepared data
  view and lab environment; it is not the frozen winning final-retrain recipe.
- BeatThis is the primary candidate; MSCNN is a lower-priority secondary
  adapter. BeatFM remains disabled until its source revision, environment,
  preprocessing, adapter, and checkpoint are audited.
- Final seed/epoch, allowed-validation decision, final all-allowed-data
  retrain, checkpoint hash, and one-WAV smoke test are **pending**. No script
  or README here asserts that a final MIREX model has already been submitted.

Never evaluate a checkpoint on pieces used for its training. The gate and
corrected diagnostic are documented in [`../scripts/`](../scripts/) and
[`../results/`](../results/).
