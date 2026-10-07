# Checkpoint files

Put downloaded Release checkpoints in this folder alongside the included
`tcn-mirex.ckpt`. Filenames must match the six `--backbone` choices:

| Filename | Source | Availability |
|---|---|---|
| `beatthis-mirex.ckpt` | no-SMC/no-GTZAN, seed 2, epoch 119 | `mirex-ckpts.zip` |
| `mscnn-mirex.ckpt` | no-SMC/no-GTZAN, seed 0, epoch 1499 | `mirex-ckpts.zip` |
| `tcn-mirex.ckpt` | no-SMC/no-GTZAN, seed 0, epoch 119 | included here and in `mirex-ckpts.zip` |
| `beatthis-icassp.ckpt` | upstream eight-fold fold 0 | ICASSP fold-0 package, pending complete verification |
| `mscnn-icassp.ckpt` | eight-fold fold 0 | ICASSP fold-0 package, pending complete verification |
| `tcn-icassp.ckpt` | eight-fold fold 0 | ICASSP fold-0 package, pending complete verification |

The MIREX exports retain original-precision model tensors and inference
hyperparameters; training optimizer and scheduler state was removed without
quantization. The ICASSP package will contain only fold-0 examples—never
claim that three files reproduce the eight-fold paper table. The upstream
BeatThis `final0` weight is not a fold-0 weight and must not be substituted.
