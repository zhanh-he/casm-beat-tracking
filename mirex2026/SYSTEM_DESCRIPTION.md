# CASM systems for MIREX 2026 Audio Beat Tracking

## Scope

The competition package shares one audio-to-activation contract across three
planned neural frontends: BeatThis, MSCNN, and BeatFM. Each frontend returns
50 Hz beat and downbeat logits. The user can then choose Direct peak picking,
the joint madmom DBN, or Confidence-Adaptive Semi-Markov (CASM) decoding.

BeatThis is the primary current system. MSCNN is retained as a lightweight
secondary comparison. BeatFM will be enabled only after its upstream source
revision, preprocessing, checkpoint loader, and no-SMC weights have been
audited. The source tree contains an explicit disabled registry entry until
those materials are available.

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
allowed validation datasets. Diagnostic target-set results are generated only
after this freeze and cannot change the compliant recommendation.

For the final competition model, the selected seed and training duration are
retrained using all allowed training and validation data. This corresponds to
the final-model protocol rather than the ICASSP eight-fold protocol.

## Reproducibility fields still to freeze

The following are intentionally placeholders until the running experiments
finish:

- BeatThis final checkpoint path, epoch, seed, and SHA-256;
- MSCNN final checkpoint path, epoch, seed, and SHA-256;
- BeatFM upstream revision, environment, adapter, training recipe, checkpoint,
  and SHA-256;
- final list of MIREX command lines;
- training compute and inference-time declaration.

The archive builder refuses to overwrite an existing bundle and writes a
SHA-256 manifest for all supplied artifacts.
