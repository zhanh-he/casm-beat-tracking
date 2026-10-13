# MIREX 2026 three-backbone technical handoff — 2026-10-07

The two archives below are separate task entries. Upload the archive for the
matching task; do not use the older BeatFM or full-retrain bundles by mistake.
Each archive has a task-specific `README.md` with exactly nine organizer
commands: BeatThis/MSCNN/TCN × CASM/DBN55–215/DBN30–300.

| Task | Archive | SHA-256 |
|---|---|---|
| Audio Beat Tracking | `submission-builds/casm-mirex2026-beat-three-backbone-slim-READY-20261007.tar.gz` | `b61e5b747b156e50de673d60cf0ea75944c2b6ee802aa61564d355cc0925eb8e` |
| Audio Downbeat Estimation | `submission-builds/casm-mirex2026-downbeat-three-backbone-slim-READY-20261007.tar.gz` | `b91bc3ab454b77c35a318b91862dba1e842d05e379213b8fad95546e5876706c` |

The two archives contain the same three allowed-validation-selected split
weights, not any full-allowed-data retrain:

| Model | Frozen choice | SHA-256 |
|---|---|---|
| BeatThis | seed 2, zero-based epoch 119 | `3bcd54a331076fcc406c68d155a43d0ed3770808d175f87372ced9bd9ca1cd6e` |
| MSCNN | seed 0, zero-based epoch 1499 | `b097cf28de56884129fff16a5e3353ab06c939ecc3aed4c5b9c03d97b73d7f3d` |
| TCN | seed 0, zero-based epoch 119 | `151779e89ad3ba3b8a221ee7f166746cbb95a8aef78fa570eea75c85bd2c5bfe` |

These are lossless, original-precision inference exports. The source
Lightning checkpoints were 243/15/0.9 MB; the published exports are
81.1/5.2/0.3 MB. See [`weights/README.md`](weights/README.md) for the exact
source/export hash mapping and the no-SMC/no-GTZAN protocol distinction.

## Technical acceptance

- Both final archives passed gzip/tar integrity checks; every file was
  rehashed against its archive's `MANIFEST.json`. Both were copied to
  lab5090, hash-checked, extracted, and smoke-run there.
- The 44.1 kHz/16-bit/mono WAV test passed all **18** task × backbone ×
  decoder combinations on Ubuntu 22.04.5 LTS. The result files were checked
  for ASCII numeric lines, strictly increasing seconds, no headers, and
  timestamps within the 31.788-second input.
- `install.sh` created a new Python 3.11 virtual environment on lab5090;
  all 18 combinations passed again using its installed dependencies, without
  relying on the pre-existing experiment environment. CPU fallback was also
  smoke-tested for BeatThis + CASM.
- The inference exports retained every model tensor bitwise and removed only
  trainer-side state. All 18 fresh-environment output files compared
  byte-for-byte equal with the original checkpoints. The slim archives have
  file-hash manifests and retain the `_mirex.ckpt` filenames throughout.

## Audio-input verification against the 2026 task specifications

Both official task pages specify a **single 44.1 kHz, 16-bit PCM, mono WAV**
as input and a caller-supplied full path for an ASCII output file containing
one event time in seconds per line. The tested WAV was confirmed as RIFF/WAVE,
PCM_16, mono, 44,100 Hz, 1,401,848 samples (31.7879365 seconds). Inside the
freshly installed Linux submission environment, the packaged BeatThis loader
read that file, downsampled it with `soxr` to 22,050 Hz (700,924 samples), and
generated a finite **1,590-frame × 128-bin log-Mel** tensor at 50 frames/s.
The actual `Audio2Frames.signal2spect` output matched a separately invoked
packaged `LogMelSpect` calculation with maximum absolute difference **0.0**;
its beat and downbeat logits both had 1,590 finite frames. BeatThis and MSCNN
share this exact loader. TCN uses the same packaged `load_audio`, `soxr`, and
`LogMelSpect` frontend before its 128-to-74-band adapter.

The 18 archived outputs from the two task-specific slim bundles were
rechecked as ASCII numerical lines: 3 backbones × 3 postprocessors × 2 tasks;
all 18 had strictly increasing finite timestamps in [0, 31.7879365] seconds,
with no header or extra columns. This is an input/output contract and runtime
smoke test, not a claim about hidden-set accuracy. The public downbeat scorer
is still listed as TBA by the organizer.
An additional CPU invocation supplied an absolute output path containing
spaces and a nonexistent parent directory; the runner created the directory,
wrote 43 beat lines, and produced a file byte-identical to the earlier
BeatThis + CASM output.

## Submission-policy check before upload

The official MIREX 2026 task pages require a packaged algorithm and a README
with contact details and full `%input`/`%output` commands; both archives
provide these. The organizer's public evaluation repository still marks the
downbeat evaluator as TBA, so no public end-to-end official downbeat scorer
test is possible at this point.

MIREX forbids using any SMC or GTZAN split for training, validation, model
selection, parameter tuning, or any other development purpose. The frozen
seed/epoch records used only allowed validation, but historical research
diagnostics on those target datasets were viewed in this project. The person
submitting must ensure that the **decision to use these split weights and nine
variants** was not made using those diagnostics. Do not describe a
target-informed decision as allowed-validation-only. The competition's
extended abstract should accurately disclose dataset usage and the frozen
selection protocol. Uploading to the organizer has not been performed here.
