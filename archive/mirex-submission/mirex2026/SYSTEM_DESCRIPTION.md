# CASM systems for MIREX 2026 Audio Beat Tracking and Downbeat Estimation

## Scope

This is a MIREX competition system, not a repeat submission of the ICASSP
2027 conference paper. The paper submits the CASM decoding methodology and
its eight-fold experiments; this system applies CASM to separately retrained
competition backbones. BeatThis model code comes from the upstream CPJKU Beat
This repository, not from a new architecture proposed here.

The competition package shares one audio-to-activation contract across three
planned neural frontends: BeatThis, MSCNN, and BeatFM. Each frontend returns
50 Hz beat and downbeat logits. Separate `--task beat` and `--task downbeat`
entries select which event stream is written. The user can then choose Direct peak picking,
the joint madmom DBN, or Confidence-Adaptive Semi-Markov (CASM) decoding.

BeatThis is the primary current system. MSCNN is retained as a lightweight
secondary comparison. BeatFM's provided source ZIP, preprocessing, private
MERT revision, and checkpoint loader are audited. A 911-piece Ballroom/RWC
no-SMC subset completed training, and its epoch-15 train-split weight was
selected using 137 allowed validation pieces. A 1,684-piece expanded subset
finished training, but its matched-panel screen was stopped by project
decision. The
BeatFM source ZIP has no resolvable Git commit or redistribution license, so
no bundle containing it may be externally distributed without a rights check.
These reduced-data runs cannot be portrayed as equal-data BeatThis comparisons
or exact reproductions of the BeatFM paper.

## Decoder defaults

- Direct uses the BeatThis local-maxima rule and imposes no tempo range.
- DBN uses 3/4 meters and the established 55–215 BPM default. An exploratory
  command-line flag changes only the DBN tempo range to 30–300 BPM.
- CASM uses one global no-SMC configuration with a 30–300 BPM range. It has no
  learned neural weights, per-track fitting, or inference-time randomness.

## Development protocol

SMC and GTZAN are excluded from training, validation, model selection,
checkpoint selection, seed selection, CASM calibration, and all other system
development decisions. A clean seed/checkpoint decision is frozen using only
allowed validation datasets. SMC/GTZAN scores are not generated as part of
the MIREX 2026 development protocol; earlier screens are historical and
cannot change the compliant recommendation.

The primary BeatThis seed and duration were frozen on allowed validation and
retrained using all allowed training and validation data. MSCNN and BeatFM
currently retain declared train/validation-split weights; do not describe them
as full-allowed-data retrains.

## Reproducibility and remaining submission decisions

- BeatThis: seed 2, 120-epoch full-allowed retrain; checkpoint SHA-256
  `0fed3858ac75ec716e622c0a5bd50ee1345fb1443902d3024ecff5e88fa20053`.
- MSCNN: seed 0, train-split last epoch 1499; checkpoint SHA-256
  `6cb647407caf367e1e3e66d13061a4459899f26e1ae0001e5c519cac95ab30b1`.
- BeatFM: 911-piece train-split epoch 15 was selected from five candidates
  using Direct beat F/CMLt/AMLt on the 137-piece allowed Ballroom/RWC panel;
  checkpoint SHA-256
  `44a1a33f6c3d08180bea2f0619c16a39a756644f101d0cd5d1691f7abd8ba764`.
  It is a reduced-data candidate, not a full-allowed-data retrain. The
  expanded 1,684-piece training finished, but its common-panel checkpoint
  screen was cancelled after a pre-scoring staging failure; retry `70943`
  never ran.
- Freeze the final organizer command lines, BeatFM redistribution decision,
  training compute, and inference-time declaration after candidate selection.

The archive builder refuses to overwrite an existing bundle and writes a
SHA-256 manifest for all supplied artifacts.
