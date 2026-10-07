# CASM MIREX 2026 — @TASK_TITLE@

This archive is a self-contained inference entry for **@TASK_TITLE@**. It
contains three frozen no-SMC backbones (BeatThis, MSCNN, TCN) and three
selectable postprocessors (CASM, DBN 55–215 BPM, DBN 30–300 BPM). This is a
MIREX competition entry applying the CASM postprocessor; it is not a repeat
submission of the ICASSP 2027 methodology paper. BeatThis architecture and
log-Mel preprocessing come from the CPJKU Beat This project.

## Installation and input/output

Target: Linux x86_64, Python 3.11. From the extracted archive directory, run
`./install.sh` once; this creates a local `.venv` and installs pinned packages.
The organizer supplies **one** 44.1 kHz, 16-bit, mono PCM WAV and a **full
output filename** per invocation. The program writes an ASCII text file with
one @EVENT@ time in seconds per line, strictly increasing, and creates the
output directory when necessary. It writes no header, label, or beat index.
On an NVIDIA GPU the runtime chooses CUDA automatically; CPU fallback is
available. Set `MIREX_DEVICE=cpu` to force CPU. No training data, internet
access, service, or API key is required at inference time.

## Organizer commands

Run each desired line from the extracted archive directory. Every line is a
separate model/decoder variant; the organizer replaces the two placeholders
with full input and output paths. These nine lines are the **@TASK_TITLE@ task
only**—use the separately labelled archive for the other task.

```text
./run.sh --task @TASK@ --backbone beatthis --decoder casm %input %output
./run.sh --task @TASK@ --backbone beatthis --decoder dbn55_215 %input %output
./run.sh --task @TASK@ --backbone beatthis --decoder dbn30_300 %input %output
./run.sh --task @TASK@ --backbone mscnn --decoder casm %input %output
./run.sh --task @TASK@ --backbone mscnn --decoder dbn55_215 %input %output
./run.sh --task @TASK@ --backbone mscnn --decoder dbn30_300 %input %output
./run.sh --task @TASK@ --backbone tcn --decoder casm %input %output
./run.sh --task @TASK@ --backbone tcn --decoder dbn55_215 %input %output
./run.sh --task @TASK@ --backbone tcn --decoder dbn30_300 %input %output
```

For a quick check after installation, run
`./run.sh --list-backbones` and replace the two MIREX
placeholders in any line above with a local WAV and a writable output path.
`direct` is also supported for research comparisons but is not one of the
nine requested evaluation variants. CASM uses one globally frozen no-SMC
30–300 BPM configuration; DBN uses the stated BPM ranges.

## Checkpoint and data provenance

All three models were trained on the same BeatThis log-Mel pool with SMC and
GTZAN excluded, unlike earlier eight-fold or upstream benchmark weights that
may include SMC in their training folds. MIREX prohibits use of its test
datasets for development; our exact split is not prescribed by the organizer.
This archive deliberately contains **train/validation-split
weights**, not full-data retrains: 3,783 allowed training pieces and a
separate 556-piece allowed validation pool. Selection used Direct decoding
on the allowed-validation Beatles subset (27 annotated pieces) with a frozen
score: 60% beat + 40% downbeat; within each, 50% F-measure + 25% CMLt +
25% AMLt. SMC and GTZAN were not used for training, validation, checkpoint
selection, or CASM calibration. BeatThis is seed 2/zero-based epoch 119;
MSCNN is seed 0/epoch 1499; TCN is seed 0/epoch 119. The full checkpoint
identities and SHA-256 file hashes are in `MANIFEST.json`. These checkpoint
files contain only the original-precision model tensors, inference
hyperparameters, and provenance; trainer/optimizer states were removed
without quantization. The numerical
selection scores in the repository are development-set results, not MIREX
test results. Dataset provenance and third-party notices are in
`SYSTEM_DESCRIPTION.md` and `THIRD_PARTY.md`.

Contact: Zhanh He, via
[zhanh-he/casm-beat-tracking](https://github.com/zhanh-he/casm-beat-tracking/issues).
