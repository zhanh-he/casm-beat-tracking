# Audio-to-beat inference

This directory turns one audio file into a text file of beat or downbeat
times. CASM can also run by itself on stored activations; see
[`../casm/README.md`](../casm/README.md). The MIREX 2026 entry applies CASM
to separately retrained no-SMC/no-GTZAN backbones. It is a competition
application of the ICASSP 2027 CASM method, not a repeat paper submission.

## Install checkpoints

Download `mirex-ckpts.zip` from the [checkpoint Release](https://github.com/zhanh-he/casm-beat-tracking/releases)
and extract its checkpoint files into [`weights/`](weights/), **beside the
included `tcn-mirex.ckpt`**. The same folder is the destination for
`icassp-ckpts.zip` when the fold-0 set is published. Extract the ZIP contents
directly, without an extra directory level. File identities and current
availability are documented in [`weights/README.md`](weights/README.md).

The six model names are:

| Model option | Weight protocol |
|---|---|
| `beatthis-icassp` | BeatThis fold 0; train folds 1–7, test fold 0 |
| `mscnn-icassp` | MSCNN fold 0; train folds 1–7, test fold 0 |
| `tcn-icassp` | TCN fold 0; train folds 1–7, test fold 0 |
| `beatthis-mirex` | MIREX allowed-validation selection; no SMC/GTZAN development |
| `mscnn-mirex` | MIREX allowed-validation selection; no SMC/GTZAN development |
| `tcn-mirex` | MIREX allowed-validation selection; no SMC/GTZAN development |

The ICASSP fold-0 choices are **examples of one held-out fold**, not a
substitute for all eight weights or the paper's aggregate table. The MIREX
3,783/556 training/validation split is our experimental choice, not a split
mandated by the organizer. The two sets are never interchanged.

## Run

Use Linux x86-64 with Python 3.11. `./install.sh` creates a local `.venv`.
Input is one WAV; output is a UTF-8 text file containing one time in seconds
per line. The output directory is created if needed. CUDA is used when
available, otherwise CPU; set `MIREX_DEVICE=cpu` to force CPU.

```bash
cd mirex2026
./install.sh
./run.sh --list-backbones
./run.sh --task beat --backbone beatthis-mirex --decoder casm input.wav beats.txt
./run.sh --task downbeat --backbone tcn-mirex --decoder dbn55_215 input.wav downbeats.txt
```

`--decoder` accepts `direct`, `casm`, `dbn55_215`, or `dbn30_300` (also the
legacy `dbn` alias). CASM automatically uses the paper's frozen 7F default
for `*-icassp` and the frozen no-SMC configuration for `*-mirex`; an explicit
`--casm-config` can override it. DBN ranges are 55–215 or 30–300 BPM.
`--checkpoint` accepts an explicit local path for a model-specific test.

Only the small inference source is present here. Training audio, dataset
annotations, research job scripts, optimizer state, and hidden MIREX test
data are not shipped. The vendored inference slice of BeatThis retains its
MIT license in [`third_party/beat_this/LICENSE`](third_party/beat_this/LICENSE).
