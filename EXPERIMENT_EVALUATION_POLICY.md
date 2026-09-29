# Experiment evaluation gate

An accuracy number may enter a *backbone held-out* result table only when the
evaluated audio pieces were absent from the model checkpoint's training data.
For a *fully held-out pipeline* claim, they must also be absent from checkpoint
selection and postprocessor calibration. CASM's released 7F configuration was
selected on SMC folds 1–7, so an SMC result using that configuration is not a
fully held-out CASM result even with a no-SMC backbone. This applies to
BeatThis, MSCNN, TCN, BeatFM, and every future backbone. A `final0` checkpoint
is not an eight-fold checkpoint simply because its seed is zero.

Before running inference, record the checkpoint hash and its training
dataset/piece inventory. Check the evaluation piece inventory against it:

- If a complete dataset was used for training, that checkpoint has no
  benchmark row on that dataset.
- For eight-fold cross-validation, each piece must be evaluated with the
  checkpoint that held out its own fold. Concatenating predictions from those
  fold checkpoints is allowed only after verifying this mapping piece by
  piece.
- If training provenance is missing or a train/evaluation overlap is found,
  stop before inference. The aggregation step repeats the check and rejects
  already-existing invalid rows.
- If decoder calibration or checkpoint selection overlaps evaluation, label
  the row as a development diagnostic; never call it a fully held-out test.
- For MIREX 2026, SMC and GTZAN are diagnostic panels only. Seed, epoch,
  decoder, and calibration choices use allowed validation data before those
  diagnostic panels are opened.

The official BeatThis `final0` was trained on all available datasets except
GTZAN, including every SMC piece. Its SMC training-set score is not a valid
comparison and was removed from the MIREX baseline artifact. The BeatThis
`fold0`–`fold7` checkpoints have a different training protocol; the SMC
out-of-fold result uses the held-out fold for each piece.

The MIREX comparison runner guards backbone training overlap. It does not
turn the frozen 7F CASM configuration into an SMC-independent decoder. SMC
CASM rows remain explicitly calibration-overlap diagnostics.

The current MIREX target runner enforces known checkpoint provenance in
[`mirex2026/experiments/evaluation_policy.py`](mirex2026/experiments/evaluation_policy.py).
Its report builder independently rejects raw CSV rows outside the permitted
model/dataset pairs. New model families must add explicit provenance rules
before they are evaluated.
