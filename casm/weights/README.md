# Checkpoint release plan

Checkpoint binaries are intentionally not committed to this Git repository. [`manifest.json`](manifest.json) records every currently recoverable file by size and SHA-256.

Recommended public layout:

- keep the CASM code and small manifests on GitHub;
- publish CASM-trained MSCNN-lite and TCN weights in a versioned Hugging Face model repository with a model card, license, training data/split description, architecture config, and SHA-256 manifest;
- attach the same release manifest to a tagged GitHub release and archive the tag with Zenodo for a persistent DOI;
- use Google Drive only as a mirror, not as the canonical citation/download endpoint.

Beat This checkpoints are upstream artifacts and should normally be referenced from the official Beat This download rather than re-hosted. Its authors release code and published weights under MIT. A separate licensing decision is still required for our MSCNN-lite and TCN code/weights before publication.

## Recovery status (2026-09-21)

- Beat This: all eight cross-validation checkpoints and all three GTZAN seed checkpoints are protected in `mygroup` and checksumed.
- MSCNN-lite recipe study: three selected fold-0 candidates are protected in `mygroup`; `s7_mmoe_ind` is the recorded confirmation candidate. These are not a substitute for a complete eight-fold release.
- TCN: `final0` and `final1` were recovered from scratch into `mygroup` and checksumed. `final2` and the eight fold checkpoints were not found, although their cached activations/results survive. Retraining or recovery from another backup is required before claiming a complete TCN weight release.
