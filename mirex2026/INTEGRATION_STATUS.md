# MIREX integration status

This file is the handoff boundary between running experiments and the final
submission bundle. A model is enabled in `config/backbones.json` only after
all required fields below are frozen and its one-WAV smoke test passes.

## BeatThis — primary

- [x] Upstream/fork source located and revision recorded
  (`b95c8ab0c58c2d9fcfd40508ae8dffbc05ac4f5c`).
- [x] Original Direct postprocessor matched: seven-frame local maxima,
  logit threshold zero, plateau averaging, downbeat-to-beat snapping, and the
  original raw-downbeat behavior when no beat peak exists.
- [x] Audio-to-logit adapter implemented.
- [x] No-SMC, GTZAN-held-out 100-epoch seed-0 baseline launched.
- [ ] Training complete; checkpoint hashes and epoch inventory recorded.
- [ ] Allowed-validation checkpoint/seed decision frozen.
- [ ] Winning recipe retrained on all allowed development data.
- [ ] Final checkpoint copied to `weights/beatthis.ckpt` and smoke-tested.

## MSCNN — secondary

- [x] One seed-0 training run retained.
- [x] Additional seed expansion cancelled by project decision.
- [ ] Seed-0 training and screening complete.
- [ ] Exact preprocessing and checkpoint loader audited.
- [ ] `mirex_pipeline.mscnn_backend:MSCNNBackend` implemented and registered.
- [ ] Final checkpoint copied to `weights/mscnn.ckpt` and smoke-tested.

## BeatFM — reserved next candidate

- [ ] Source directory and immutable upstream revision supplied.
- [ ] License and redistribution constraints checked.
- [ ] Python/CUDA environment exported.
- [ ] Audio preprocessing, sample rate, frame rate, and output semantics
  documented.
- [ ] Checkpoint loader and inference entry point identified.
- [ ] A 50 Hz beat/downbeat-logit adapter implemented and registered.
- [ ] No-SMC training/split recipe frozen.
- [ ] Final checkpoint copied to `weights/beatfm.ckpt` and smoke-tested.

BeatFM remains intentionally disabled until these fields are known. The
pipeline will raise an explicit error instead of guessing an incompatible
adapter.

## Decoder contract

- `direct`: original BeatThis local-maxima rule, without a tempo prior.
- `dbn`: 55–215 BPM by default; `--dbn-wide` selects 30–300 BPM.
- `casm`: frozen no-SMC configuration at 30–300 BPM.

All three decoders consume one-dimensional, finite beat and downbeat logits at
the frame rate declared by the backbone registry. MIREX output contains one
strictly increasing beat time in seconds per line.
