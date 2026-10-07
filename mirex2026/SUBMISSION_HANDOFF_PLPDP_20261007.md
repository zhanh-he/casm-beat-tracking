# MIREX 2026 PLPDP-enabled task bundles — 2026-10-07

These **local** archives supersede the earlier three-decoder slim archives
listed in `SUBMISSION_HANDOFF_20261007.md`. Upload one archive per matching
MIREX task. Each task README contains exactly twelve `%input %output` command
lines: BeatThis/MSCNN/TCN × CASM/DBN55–215/DBN30–300/PLPDP. Direct remains
available for research but is not listed as an organizer variant.

| Task | Local archive | SHA-256 |
|---|---|---|
| Audio Beat Tracking | `submission-builds/casm-mirex2026-beat-three-backbone-plpdp-READY-20261007.tar.gz` | `9735f6a904c82e504d1dd1a01491a93f22bab211311886cbbfadb31a18c62205` |
| Audio Downbeat Estimation | `submission-builds/casm-mirex2026-downbeat-three-backbone-plpdp-READY-20261007.tar.gz` | `35f580314344471bb6255ca69f69f6653991c45b90996ddf1438eba4b98d7b86` |

The weights are unchanged original-precision inference exports: BeatThis seed
2/epoch 119 (`3bcd54a331076fcc406c68d155a43d0ed3770808d175f87372ced9bd9ca1cd6e`),
MSCNN seed 0/epoch 1499 (`b097cf28de56884129fff16a5e3353ab06c939ecc3aed4c5b9c03d97b73d7f3d`),
and TCN seed 0/epoch 119 (`151779e89ad3ba3b8a221ee7f166746cbb95a8aef78fa570eea75c85bd2c5bfe`).
All are train/validation-split no-SMC, no-GTZAN weights; none is the later
full-allowed-data retrain.

## Acceptance record

- Both corrected archives were hash-checked after transfer to lab5090 and
  extracted on Ubuntu 22.04.5 LTS. `install.sh` completed in a new Python
  3.11 environment containing the pinned PLPDP and DBN dependencies.
- The first build used the wrong CASM source root. It was caught by the
  full-matrix smoke test, preserved locally with `INVALID-casm-source` in its
  name, and **must not be submitted**. `build_submission.py` now rejects an
  incomplete CASM source *before* creating any output directory. The archive
  hashes above identify the rebuilt, corrected packages.
- The corrected packages passed all **24** task × backbone × postprocessor
  commands on a 44.1 kHz/16-bit/mono WAV. All 24 ASCII files contained finite,
  strictly increasing seconds within the 31.7879365-second input, with no
  header or extra columns. All 18 pre-existing CASM/DBN outputs were
  byte-identical to the earlier validated slim archives.
- Three representative commands (BeatThis+CASM beat, MSCNN+PLPDP downbeat,
  TCN+DBN55–215 beat) were rerun with the *newly installed* Python environment
  and produced byte-identical outputs to the full-matrix test. The PLPDP
  adapter's beat and downbeat outputs were also array-identical to the
  earlier audited StructBeat adapter on a frozen activation cache from each
  of the three backbones.
- The reference PLPDP source is MIT-licensed commit
  `30df4300849c843a7533e995113f4d26cd1e7d12`; its `modules.py` hash is
  `c581158c0b2fe06abfaf7e3dd9c629f344625f699ad38e2a68b8ab4f79751c49`.
  It uses the released 30–300 BPM settings and the same 50-to-100-fps adapter
  as the project's ICASSP comparison. No training audio, annotation, or
  external service is needed at inference time.

These are runtime and format checks, not official hidden-set scores. The
post-freeze GTZAN/SMC table in `results/plpdp_default_20261007/` is a
research diagnostic only. The 2026 rules forbid using either test collection
for any competition model/decoder decision; the submitter must verify that
the chosen entries and wording reflect the allowed-validation provenance.
