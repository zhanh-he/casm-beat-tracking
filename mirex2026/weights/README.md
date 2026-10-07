# MIREX 2026 inference weights

These three `_mirex.ckpt` files are the no-SMC/no-GTZAN **allowed-validation-
selected split weights** for the MIREX 2026 beat and downbeat entries. They
are not the ICASSP 2027 eight-fold weights and not the upstream BeatThis
`final0` weight: those other protocols can include SMC in training, whereas
the 2026 Beat Tracking task prohibits using any SMC or GTZAN split for
development. The exact 3,783/556 split is our training choice, **not** a
split prescribed by MIREX. The same 50 Hz BeatThis log-Mel pool was used for
all three backbones.

| File | Frozen choice | Bytes | SHA-256 |
|---|---|---:|---|
| `beatthis_mirex.ckpt` | seed 2, zero-based epoch 119 | 81,065,904 | `3bcd54a331076fcc406c68d155a43d0ed3770808d175f87372ced9bd9ca1cd6e` |
| `mscnn_mirex.ckpt` | seed 0, zero-based epoch 1499 | 5,164,753 | `b097cf28de56884129fff16a5e3353ab06c939ecc3aed4c5b9c03d97b73d7f3d` |
| `tcn_mirex.ckpt` | seed 0, zero-based epoch 119 | 295,309 | `151779e89ad3ba3b8a221ee7f166746cbb95a8aef78fa570eea75c85bd2c5bfe` |

We selected the seed/epoch candidates using Direct beat/downbeat metrics on
27 Beatles pieces within the 556-piece allowed validation pool. The fixed
score was 60% beat + 40% downbeat; each part used 50% F-measure, 25% CMLt,
25% AMLt. Training used 3,783 other allowed pieces. The source and
selection evidence is under `../results/`.

These are **lossless inference exports** of the original Lightning
checkpoints: `hyper_parameters`, original-dtype `model.*` tensors, epoch, and
provenance metadata are retained; optimizer, scheduler, callbacks, trainer
loops, and datamodule state are removed. No FP16 conversion or quantization
was applied. Every retained tensor compared bitwise equal to its source, and
all 18 beat/downbeat × backbone × decoder WAV outputs compared byte-for-byte
equal with the full training checkpoints on the Linux smoke test.
The [machine-readable manifest](manifest.json) records file sizes, source
hashes, and the frozen seed/epoch choices.

The exports were made with `../scripts/export_inference_ckpt.py`. Their
source checkpoint SHA-256 values are, respectively,
`cd8a8c93b11c189daab497076261730bc8a059fa2b8d2b9c07b012c2d9c4bd4d`,
`6cb647407caf367e1e3e66d13061a4459899f26e1ae0001e5c519cac95ab30b1`,
and `4b55dd02e63560bbc06b6800f48cf3c1eeac21b4af003a9f82f4b86fdb395b4f`.

These checkpoint files alone are not an executable submission. The task
archives built by `../build_submission.py` also include the runnable frontend,
decoders, dependency installer, task-specific README, and file manifest.
