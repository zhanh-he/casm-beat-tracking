# Checkpoint files

Put downloaded Release checkpoints in this folder alongside the included
`tcn-mirex.ckpt`. Filenames must match the six `--backbone` choices:

| Filename | Source | Availability |
|---|---|---|
| `beatthis-mirex.ckpt` | no-SMC/no-GTZAN, seed 2, epoch 119 | `mirex-ckpts.zip` |
| `mscnn-mirex.ckpt` | no-SMC/no-GTZAN, seed 0, epoch 1499 | `mirex-ckpts.zip` |
| `tcn-mirex.ckpt` | no-SMC/no-GTZAN, seed 0, epoch 119 | included here and in `mirex-ckpts.zip` |
| `beatthis-icassp.ckpt` | upstream eight-fold fold 0 | Not in the current Release; request by email. |
| `mscnn-icassp.ckpt` | eight-fold fold 0 | Not in the current Release; request by email. |
| `tcn-icassp.ckpt` | eight-fold fold 0 | Not in the current Release; request by email. |

The MIREX exports retain original-precision model tensors and inference
hyperparameters; training optimizer and scheduler state was removed without
quantization. The current public Release provides `mirex-ckpts.zip`, not an
ICASSP checkpoint ZIP. Additional ICASSP checkpoints can be requested through
the contact in the root README. One fold-0 example per backbone does not
reproduce the eight-fold paper table. The upstream BeatThis `final0` weight
is not a fold-0 weight and must not be substituted.
